
from src.eligibility import check_eligibility


def candidate(text):
    """Create a mock candidate for testing."""
    return {
        "candidate_name": "Test Candidate",
        "text": text,
    }


def test_valid_python_ai_candidate():
    result = check_eligibility(candidate(
        "Skills: Python, FastAPI. "
        "Built a RAG pipeline using FAISS and embeddings."
    ))

    assert result["eligible"] is True
    assert "Python" in result["matched_skills"]
    assert result["rejection_reasons"] == []


def test_no_python():
    result = check_eligibility(candidate(
        "Skills: JavaScript, React. "
        "Developed a RAG application using LangChain."
    ))

    assert result["eligible"] is False
    assert "No evidence of Python stack" in result["rejection_reasons"]


def test_no_ai_project():
    result = check_eligibility(candidate(
        "Skills: Python, Django, PostgreSQL. "
        "Built an inventory management REST API."
    ))

    assert result["eligible"] is False
    assert (
        "No meaningful AI/agentic implementation evidence"
        in result["rejection_reasons"]
    )


def test_ai_interest_only():
    result = check_eligibility(candidate(
        "Skills: Python. "
        "Interests: Artificial Intelligence and LLMs."
    ))

    assert result["eligible"] is False


def test_mixed_stack():
    result = check_eligibility(candidate(
        "Skills: JavaScript, React, Java, Python. "
        "Developed an AI document assistant using "
        "LangChain and vector search."
    ))

    assert result["eligible"] is True


def test_python_interest_only():
    result = check_eligibility(candidate(
        "Interested in learning Python. "
        "Built a RAG pipeline using LangChain."
    ))

    assert result["eligible"] is False


def test_python_in_project():
    result = check_eligibility(candidate(
        "Projects: Developed a RAG chatbot using "
        "Python, LangChain, and FAISS."
    ))

    assert result["eligible"] is True
