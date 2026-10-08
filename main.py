from src.parser import parse_directory
from src.eligibility import check_eligibility
from src.scorer import score_candidate
from src.github_service import GitHubEnricher


def main():
    candidates = parse_directory("resumes")

    github_service = GitHubEnricher()

    ranked_candidates = []
    rejected_candidates = []
    failed_candidates = []

    for candidate in candidates:

        if candidate["status"] != "success":
            failed_candidates.append(candidate)
            continue

        eligibility = check_eligibility(candidate)

        if not eligibility["eligible"]:
            rejected_candidates.append(eligibility)
            continue

        # Enrich only eligible candidates.
        github_data = github_service.enrich(
            candidate.get("github_url")
        )

        result = score_candidate(
            candidate,
            eligibility,
            github_score=github_data["score"]
        )

        result["github_status"] = github_data["status"]
        result["github_summary"] = github_data["summary"]
        result["github_url"] = candidate.get("github_url")
        result["filename"] = candidate["filename"]

        ranked_candidates.append(result)

    ranked_candidates.sort(
        key=lambda item: (
            -item["total_score"],
            -item["score_breakdown"]["ai_project_depth"],
            item["filename"],
        )
    )

    for rank, candidate in enumerate(
        ranked_candidates, start=1
    ):
        candidate["rank"] = rank

    print("\n===== SCREENING SUMMARY =====")
    print("Total:", len(candidates))
    print("Eligible:", len(ranked_candidates))
    print("Rejected:", len(rejected_candidates))
    print("Failed:", len(failed_candidates))

    print("\n===== TOP 5 RANKED CANDIDATES =====")

    for candidate in ranked_candidates[:5]:
        print("\nRank:", candidate["rank"])
        print("Name:", candidate["candidate_name"])
        print("Total Score:", candidate["total_score"])
        print("Breakdown:", candidate["score_breakdown"])
        print("GitHub Status:", candidate["github_status"])
        print("GitHub:", candidate["github_summary"])
        print("Strengths:", candidate["strengths"])
        print("Concerns:", candidate["concerns"])
        print("-" * 50)


if __name__ == "__main__":
    main()
