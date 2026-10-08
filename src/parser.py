from pathlib import Path
import re
import pymupdf


EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"
)

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/"
    r"([A-Za-z0-9-]+)",
    re.IGNORECASE
)

GITHUB_RESERVED = {
    "topics", "features", "explore", "settings",
    "login", "signup", "orgs", "marketplace"
}


def extract_text(pdf_path):
    """Extract text from every page of a PDF."""
    pages = []

    with pymupdf.open(pdf_path) as document:
        for page in document:
            text = page.get_text("text", sort=True)
            pages.append(text)

    return "\n".join(pages).strip()


def extract_email(text):
    """Find the first email address."""
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_github(text):
    """Find a GitHub user profile URL."""
    for match in GITHUB_PATTERN.finditer(text):
        username = match.group(1)

        if username.lower() not in GITHUB_RESERVED:
            return f"https://github.com/{username}"

    return None


def extract_name(text):
    """Use the first plausible heading as a name."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:8]:
        if (
            2 <= len(line.split()) <= 4
            and len(line) <= 60
            and not any(char.isdigit() for char in line)
            and "@" not in line
            and "http" not in line.lower()
            and re.fullmatch(r"[A-Za-z .'-]+", line)
        ):
            return line.title()

    return None


def parse_resume(pdf_path):
    """
    Parse one resume and return a consistent result.
    Never propagate a PDF parsing error to the batch.
    """
    pdf_path = Path(pdf_path)

    try:
        text = extract_text(pdf_path)

        if not text:
            raise ValueError("No extractable text found")

        return {
            "filename": pdf_path.name,
            "candidate_name": extract_name(text),
            "email": extract_email(text),
            "github_url": extract_github(text),
            "text": text,
            "status": "success",
            "error": None,
        }

    except Exception as exc:
        return {
            "filename": pdf_path.name,
            "candidate_name": None,
            "email": None,
            "github_url": None,
            "text": "",
            "status": "failed",
            "error": str(exc),
        }


def parse_directory(directory):
    """Parse all PDFs in the provided directory."""
    directory = Path(directory)

    if not directory.is_dir():
        raise ValueError(
            f"Resume directory not found: {directory}"
        )

    pdf_files = sorted(directory.glob("*.pdf"))

    results = []

    for pdf_file in pdf_files:
        result = parse_resume(pdf_file)
        results.append(result)

    return results
