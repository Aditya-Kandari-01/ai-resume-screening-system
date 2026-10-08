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
    """Extract a GitHub profile URL from resume text."""
    for match in GITHUB_PATTERN.finditer(text):
        username = match.group(1)

        if username.lower() not in GITHUB_RESERVED:
            return f"https://github.com/{username}"

    return None




def extract_name(text):
    """Extract candidate names from common resume header layouts."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    excluded = {
        "skills", "skills summary", "summary",
        "professional summary", "profile",
        "education", "experience", "work experience",
        "projects", "technical skills",
        "certifications", "achievements",
        "contact", "objective", "resume",
    }

    def valid_name(value):
        normalized = value.lower().strip(": ")

        return (
            normalized not in excluded
            and 2 <= len(value.split()) <= 4
            and len(value) <= 60
            and not any(char.isdigit() for char in value)
            and re.fullmatch(r"[A-Za-z .'-]+", value)
            is not None
        )

    header = lines[:12]
    # Case 1: Name and email appear on the same line.
    for line in header:
        if "@" in line:
            before_email = EMAIL_PATTERN.split(line)[0].strip()
    
            # Remove extra contact separators.
            before_email = before_email.strip(" |-—")
    
            if valid_name(before_email):
                return before_email.title()
    
    # Case 2 : Handle split names with contact details on each line.
    # Example:
    # Prathamesh      prathameshpatil330@gmail.com
    # Patil           LinkedIn | Github

    for i in range(min(6, len(header) - 1)):
        first_line = header[i]
        second_line = header[i + 1]

        # Extract the first word from each line.
        first_match = re.match(r"^([A-Za-z'-]+)\b", first_line)
        second_match = re.match(r"^([A-Za-z'-]+)\b", second_line)

        if not first_match or not second_match:
            continue

        first_name = first_match.group(1)
        last_name = second_match.group(1)

        # First line must contain an email.
        if not EMAIL_PATTERN.search(first_line):
            continue

        # Second line should contain contact information.
        if not re.search(
            r"\blinkedin\b|\bgithub\b",
            second_line,
            re.IGNORECASE
        ):
            continue

        combined_name = f"{first_name} {last_name}"

        if valid_name(combined_name):
            return combined_name.title()


    # Case 3: Complete name appears on a separate line.
    for line in header:
        if valid_name(line):
            return line.title()

    # Case 4: First and last names on consecutive lines.
    for i in range(min(5, len(header) - 1)):
        first = header[i]
        second = header[i + 1]

        if (
            re.fullmatch(r"[A-Za-z'-]+", first)
            and re.fullmatch(r"[A-Za-z'-]+", second)
        ):
            combined = f"{first} {second}"

            if valid_name(combined):
                return combined.title()

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
        name = extract_name(text)
        return {
            "filename": pdf_path.name,
            "candidate_name": name or pdf_path.stem,
            "name_extraction_status": "failed",
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
