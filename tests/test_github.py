from datetime import datetime, timedelta, timezone

def test_github_profile_not_found():
    import requests

    class NotFoundSession:
        def get(self, *args, **kwargs):
            response = requests.Response()
            response.status_code = 404
            response.url = (
                "https://api.github.com/users/missing-user"
            )
            return response

    service = GitHubEnricher(session=NotFoundSession())

    result = service.enrich(
        "https://github.com/missing-user"
    )

    assert result["status"] == "profile_not_found"
    assert result["score"] == 0
    
from src.github_service import (
    extract_username,
    calculate_github_score,
    GitHubEnricher,
)


def iso_days_ago(days):
    return (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).isoformat()


def test_extract_username():
    assert extract_username(
        "https://github.com/example-user"
    ) == "example-user"

    assert extract_username(
        "https://evil.com/example-user"
    ) is None


def test_recent_activity():
    events = [
        {"created_at": iso_days_ago(1)}
        for _ in range(12)
    ]

    result = calculate_github_score([], events)

    assert result["activity_score"] == 4


def test_relevant_repositories():
    repos = [
        {
            "name": "ai-agent",
            "description": "Python LangGraph AI agent",
            "language": "Python",
            "topics": ["langgraph"],
            "pushed_at": iso_days_ago(10),
            "fork": False,
        },
        {
            "name": "react-portfolio",
            "description": "Personal website",
            "language": "JavaScript",
            "topics": [],
            "pushed_at": iso_days_ago(200),
            "fork": False,
        },
    ]

    result = calculate_github_score(repos, [])

    assert result["repository_score"] == 2
    assert "ai-agent" in result["relevant_repositories"]


def test_github_score_cap():
    repos = [
        {
            "name": f"python-ai-{i}",
            "description": "Python RAG agent",
            "language": "Python",
            "topics": ["rag"],
            "pushed_at": iso_days_ago(1),
            "fork": False,
        }
        for i in range(10)
    ]

    events = [
        {"created_at": iso_days_ago(1)}
        for _ in range(30)
    ]

    result = calculate_github_score(repos, events)

    assert result["score"] == 10


def test_missing_github_profile():
    service = GitHubEnricher()

    result = service.enrich(None)

    assert result["score"] == 0
    assert result["status"] == "missing_profile"


def test_api_failure_does_not_crash():
    import requests

    class FailingSession:
        def get(self, *args, **kwargs):
            raise requests.Timeout("Request timed out")

    service = GitHubEnricher(session=FailingSession())

    result = service.enrich(
        "https://github.com/example-user"
    )

    assert result["score"] == 0
    assert result["status"] == "api_error"
