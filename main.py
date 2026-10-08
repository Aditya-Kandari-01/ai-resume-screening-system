
from src.parser import parse_directory


def main():
    results = parse_directory("resumes")

    success = sum(
        r["status"] == "success" for r in results
    )

    failed = len(results) - success

    print(f"Total resumes: {len(results)}")
    print(f"Successfully parsed: {success}")
    print(f"Failed: {failed}")

    print("\nSample parsed candidates:\n")

    for candidate in results[:5]:
        print("File:", candidate["filename"])
        print("Name:", candidate["candidate_name"])
        print("Email:", candidate["email"])
        print("GitHub:", candidate["github_url"])
        print("Status:", candidate["status"])
        print("Text length:", len(candidate["text"]))
        print("-" * 40)


if __name__ == "__main__":
    main()
