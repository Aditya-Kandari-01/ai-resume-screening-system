
import json

from main import run_screening


def test_pipeline_with_synthetic_resumes(tmp_path, monkeypatch):
    fake_resumes = [
        {
            "filename": "eligible.pdf",
            "candidate_name": "Example Candidate",
            "text": (
                "Skills: Python, FastAPI. "
                "Built a RAG pipeline using FAISS."
            ),
            "github_url": None,
            "status": "success",
        },
        {
            "filename": "rejected.pdf",
            "candidate_name": "Another Candidate",
            "text": "JavaScript, React. Built a website.",
            "github_url": None,
            "status": "success",
        },
        {
            "filename": "broken.pdf",
            "candidate_name": None,
            "text": "",
            "status": "failed",
            "error": "Unreadable PDF",
        },
    ]

    monkeypatch.setattr(
        "main.parse_directory",
        lambda directory: fake_resumes
    )

    result = run_screening(
        str(tmp_path), skip_github=True
    )

    summary = result["summary"]

    assert summary["total_resumes"] == 3
    assert summary["eligible"] == 1
    assert summary["rejected"] == 1
    assert summary["failed"] == 1

    assert result["ranked_candidates"][0]["rank"] == 1
    assert result["ranked_candidates"][0]["github_status"] == "skipped"

    # Verify the result is JSON serializable.
    json.dumps(result)
