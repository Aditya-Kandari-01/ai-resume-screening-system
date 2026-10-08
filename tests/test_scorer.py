
import pytest

from src.scorer import score_candidate


def candidate(text):
    return {
        "candidate_name": "Test Candidate",
        "text": text,
    }


def test_strong_candidate():
    result = score_candidate(candidate(
        "Skills: Python, FastAPI, PostgreSQL, React, Docker. "
        "Built a RAG pipeline using FAISS and embeddings. "
        "Implemented LangGraph tool calling agents. "
        "Added model evaluation, pytest unit tests, "
        "caching and monitoring. Deployed on GCP."
    ))

    assert result["eligible"] is True
    assert result["score_breakdown"]["ai_project_depth"] == 40
    assert result["total_score"] <= 90


def test_shallow_ai_project():
    result = score_candidate(candidate(
        "Skills: Python, Flask. "
        "Built an AI chatbot using the OpenAI API "
        "for simple question answering."
    ))

    assert result["penalty"] > 0
    assert result["total_score"] < 50


def test_strong_candidate_outranks_shallow():
    strong = score_candidate(candidate(
        "Skills: Python, FastAPI, PostgreSQL, Docker. "
        "Built a RAG pipeline using FAISS, "
        "LangGraph tool calling and model evaluation. "
        "Deployed on GCP."
    ))

    shallow = score_candidate(candidate(
        "Skills: Python, Flask. "
        "Built a chatbot using the OpenAI API."
    ))

    assert strong["total_score"] > shallow["total_score"]


def test_ineligible_candidate_cannot_be_scored():
    with pytest.raises(ValueError):
        score_candidate(candidate(
            "Built a React and Node.js e-commerce website."
        ))


def test_score_category_limits():
    result = score_candidate(candidate(
        "Python FastAPI Django Flask PostgreSQL Redis "
        "MongoDB React Next.js Docker AWS GCP. "
        "Built a RAG pipeline using FAISS, LangGraph "
        "tool calling and model evaluation. "
        "Implemented caching, unit tests, logging."
    ), github_score=100)

    limits = {
        "ai_project_depth": 40,
        "python_backend": 30,
        "cloud_fullstack": 15,
        "github": 10,
        "engineering_depth": 5,
    }

    for category, maximum in limits.items():
        assert 0 <= result["score_breakdown"][category] <= maximum

    assert 0 <= result["total_score"] <= 100
