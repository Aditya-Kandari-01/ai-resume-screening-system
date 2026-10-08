from src.parser import parse_directory
from src.eligibility import check_eligibility


def main():
    candidates = parse_directory("resumes")

    eligible_candidates = []
    rejected_candidates = []
    failed_candidates = []

    for candidate in candidates:

        if candidate["status"] != "success":
            failed_candidates.append(candidate)
            continue

        result = check_eligibility(candidate)

        if result["eligible"]:
            eligible_candidates.append(result)
        else:
            rejected_candidates.append(result)

    print("\n===== SCREENING SUMMARY =====")
    print("Total:", len(candidates))
    print("Eligible:", len(eligible_candidates))
    print("Rejected:", len(rejected_candidates))
    print("Failed:", len(failed_candidates))

    print("\n===== FIRST 5 ELIGIBLE =====")

    for candidate in eligible_candidates[:5]:
        print("Name:", candidate["candidate_name"])
        print("Skills:", candidate["matched_skills"])
        print("AI evidence:", candidate["evidence"]["ai"])
        print("-" * 50)

    print("\n===== FIRST 5 REJECTED =====")

    for candidate in rejected_candidates[:5]:
        print("Name:", candidate["candidate_name"])
        print("Reasons:", candidate["rejection_reasons"])
        print("-" * 50)


if __name__ == "__main__":
    main()
