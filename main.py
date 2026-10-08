
from src.parser import parse_directory
from src.eligibility import check_eligibility
from src.scorer import score_candidate


def main():
    candidates = parse_directory("resumes")

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

        score = score_candidate(candidate, eligibility)
        ranked_candidates.append(score)

    ranked_candidates.sort(
        key=lambda candidate: candidate["total_score"],
        reverse=True
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
        print("Penalty:", candidate["penalty"])
        print("Strengths:", candidate["strengths"])
        print("Concerns:", candidate["concerns"])
        print("-" * 50)


if __name__ == "__main__":
    main()
