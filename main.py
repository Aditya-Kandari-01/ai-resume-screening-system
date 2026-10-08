
import argparse
import json
from collections import Counter
from pathlib import Path

from src.parser import parse_directory
from src.eligibility import check_eligibility
from src.scorer import score_candidate
from src.github_service import GitHubEnricher


def run_screening(input_dir, skip_github=False):
    candidates = parse_directory(input_dir)

    if not candidates:
        raise ValueError("No PDF resumes found in input directory")

    github_service = GitHubEnricher()

    eligible = []
    rejected = []
    failed = []

    for candidate in candidates:
        filename = candidate["filename"]

        if candidate["status"] != "success":
            failed.append({
                "filename": filename,
                "status": "failed",
                "error": candidate.get("error"),
            })
            continue

        try:
            eligibility = check_eligibility(candidate)

            if not eligibility["eligible"]:
                rejected.append({
                    "filename": filename,
                    "candidate_name": candidate["candidate_name"],
                    "eligible": False,
                    "rejection_reasons": eligibility["rejection_reasons"],
                    "matched_skills": eligibility["matched_skills"],
                    "evidence": eligibility["evidence"],
                })
                continue

            if skip_github:
                github = {
                    "status": "skipped",
                    "score": 0,
                    "summary": "GitHub enrichment skipped by user",
                }
            else:
                github = github_service.enrich(
                    candidate.get("github_url")
                )

            result = score_candidate(
                candidate,
                eligibility,
                github_score=github["score"],
            )

            result.update({
                "filename": filename,
                "name_extraction_status": candidate.get(
                    "name_extraction_status"
                ),
                "github_url": candidate.get("github_url"),
                "github_status": github["status"],
                "github_summary": github["summary"],
            })

            if github["status"] in {
                "api_error", "rate_limited", "skipped"
            }:
                result["concerns"].append(
                    "GitHub score unavailable; final score "
                    "may underestimate public activity."
                )

            eligible.append(result)

        except Exception as exc:
            failed.append({
                "filename": filename,
                "status": "failed",
                "error": str(exc),
            })

    # Sort by score, then AI depth, then filename.
    eligible.sort(
        key=lambda c: (
            -c["total_score"],
            -c["score_breakdown"]["ai_project_depth"],
            c["filename"],
        )
    )

    for rank, candidate in enumerate(eligible, start=1):
        candidate["rank"] = rank

    github_statuses = Counter(
        candidate["github_status"] for candidate in eligible
    )

    summary = {
        "total_resumes": len(candidates),
        "successfully_parsed": sum(
            c["status"] == "success" for c in candidates
        ),
        "eligible": len(eligible),
        "rejected": len(rejected),
        "failed": len(failed),
        "github_enrichment_status": dict(github_statuses),
    }

    assert (
        summary["total_resumes"]
        == summary["eligible"]
        + summary["rejected"]
        + summary["failed"]
    )

    return {
        "summary": summary,
        "ranked_candidates": eligible,
        "rejected_candidates": rejected,
        "failed_candidates": failed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Screening and Ranking"
    )

    parser.add_argument(
        "--input",
        default="./resumes",
        help="Directory containing PDF resumes",
    )

    parser.add_argument(
        "--output",
        default="./output/results.json",
        help="Path to JSON output",
    )

    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="Skip GitHub API calls for offline testing",
    )

    args = parser.parse_args()

    results = run_screening(
        args.input,
        skip_github=args.skip_github,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    summary = results["summary"]

    print("\n===== SCREENING SUMMARY =====")
    print("Total:", summary["total_resumes"])
    print("Parsed:", summary["successfully_parsed"])
    print("Eligible:", summary["eligible"])
    print("Rejected:", summary["rejected"])
    print("Failed:", summary["failed"])
    print(
        "GitHub statuses:",
        summary["github_enrichment_status"]
    )

    print("\n===== TOP 5 CANDIDATES =====")

    for candidate in results["ranked_candidates"][:5]:
        print(
            f"#{candidate['rank']} "
            f"{candidate['candidate_name']} "
            f"- {candidate['total_score']}/100 "
            f"(GitHub: {candidate['github_status']})"
        )

    print(f"\nResults saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
