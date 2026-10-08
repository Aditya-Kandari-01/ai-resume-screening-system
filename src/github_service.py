
import os
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE = "https://api.github.com"
TIMEOUT = float(os.getenv("GITHUB_TIMEOUT", "5"))
TOKEN = os.getenv("GITHUB_TOKEN")

RELEVANT_TERMS = (
    "python", "machine learning", "llm", "rag",
    "langchain", "langgraph", "fastapi", "pytorch",
    "tensorflow", "agent", "artificial intelligence"
)


def extract_username(profile_url):
    """Validate the URL and extract a GitHub username."""
    if not profile_url:
        return None

    try:
        parsed = urlparse(profile_url)

        if parsed.scheme not in ("http", "https"):
            return None

        if parsed.hostname not in ("github.com", "www.github.com"):
            return None

        parts = parsed.path.strip("/").split("/")
        username = parts[0]

        if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", username):
            return None

        return username

    except (ValueError, AttributeError):
        return None


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except (ValueError, TypeError):
        return None


def calculate_github_score(repos, events):
    """
    Return a GitHub score out of 10:
    5 recent activity + 5 maintained/relevant repos.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)

    recent_events = sum(
        1 for event in events
        if (date := parse_date(event.get("created_at")))
        and date >= cutoff
    )

    if recent_events >= 21:
        activity_score = 5
    elif recent_events >= 11:
        activity_score = 4
    elif recent_events >= 6:
        activity_score = 3
    elif recent_events >= 3:
        activity_score = 2
    elif recent_events >= 1:
        activity_score = 1
    else:
        activity_score = 0

    maintained = []
    relevant = []

    for repo in repos:
        if repo.get("fork"):
            continue

        updated = parse_date(repo.get("pushed_at"))

        if updated and updated >= cutoff:
            maintained.append(repo["name"])

        searchable = " ".join([
            repo.get("name") or "",
            repo.get("description") or "",
            repo.get("language") or "",
            " ".join(repo.get("topics") or []),
        ]).lower()

        if any(term in searchable for term in RELEVANT_TERMS):
            relevant.append(repo["name"])

    # Max 2 for maintained, max 3 for relevant.
    repo_score = min(2, len(maintained)) + min(
        3, len(relevant)
    )

    total = activity_score + repo_score

    return {
        "score": min(10, total),
        "activity_score": activity_score,
        "repository_score": repo_score,
        "recent_public_events": recent_events,
        "maintained_repositories": maintained[:10],
        "relevant_repositories": relevant[:10],
    }


class GitHubEnricher:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.cache = {}
        self.rate_limited = False

        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-resume-screener",
        }

        if TOKEN:
            self.headers["Authorization"] = f"Bearer {TOKEN}"

    def fetch(self, endpoint, params=None):
        response = self.session.get(
            f"{API_BASE}{endpoint}",
            headers=self.headers,
            params=params,
            timeout=TIMEOUT,
        )

        if response.status_code in (403, 429):
            self.rate_limited = True
            raise RuntimeError(
                f"GitHub API unavailable/rate-limited: "
                f"HTTP {response.status_code}"
            )

        response.raise_for_status()
        return response.json()

    def enrich(self, profile_url):
        username = extract_username(profile_url)

        if not username:
            return {
                "status": "missing_profile",
                "score": 0,
                "summary": "No valid GitHub profile available",
            }

        cache_key = username.lower()

        if cache_key in self.cache:
            return self.cache[cache_key]

        if self.rate_limited:
            return {
                "status": "rate_limited",
                "score": 0,
                "summary": "GitHub API access unavailable",
            }

        try:
            self.fetch(f"/users/{username}")

            repos = self.fetch(
                f"/users/{username}/repos",
                params={
                    "sort": "pushed",
                    "per_page": 100,
                    "type": "owner",
                },
            )

            events = self.fetch(
                f"/users/{username}/events/public",
                params={"per_page": 100},
            )

            scoring = calculate_github_score(repos, events)

            result = {
                "status": "success",
                "username": username,
                **scoring,
                "summary": (
                    f"{scoring['recent_public_events']} recent "
                    f"public events; "
                    f"{len(scoring['maintained_repositories'])} "
                    f"recently maintained repositories; "
                    f"{len(scoring['relevant_repositories'])} "
                    f"relevant repositories."
                ),
            }

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else None
            )

            result = {
                "status": (
                    "profile_not_found"
                    if status_code == 404
                    else "api_error"
                ),
                "username": username,
                "score": 0,
                "summary": (
                    "GitHub profile not found (HTTP 404)"
                    if status_code == 404
                    else f"GitHub API error: {exc}"
                ),
            }

        except requests.RequestException as exc:
            result = {
                "status": "api_error",
                "username": username,
                "score": 0,
                "summary": f"GitHub enrichment failed: {exc}",
            }

        except RuntimeError as exc:
            result = {
                "status": "rate_limited",
                "username": username,
                "score": 0,
                "summary": str(exc),
            }

        self.cache[cache_key] = result
        return result
