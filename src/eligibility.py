import re


PYTHON_PATTERN = re.compile(r"\bpython\b", re.IGNORECASE)

AI_PATTERNS = {
    "LangChain": r"\blangchain\b",
    "LangGraph": r"\blanggraph\b",
    "LlamaIndex": r"\bllamaindex\b",
    "Google ADK": r"\bgoogle\s+adk\b",
    "RAG": r"\brag\b|\bretrieval.augmented generation\b",
    "FAISS": r"\bfaiss\b",
    "ChromaDB": r"\bchromadb\b|\bchroma\s*db\b",
    "Vector Search": r"\bvector\s+(?:search|database|db)\b",
    "Embeddings": r"\bembeddings?\b",
    "Tool Calling": r"\btool[\s-]+calling\b",
    "Multi-Agent": r"\bmulti[\s-]+agent\b",
    "LLM": r"\bllms?\b|\blarge language models?\b",
    "OpenAI": r"\bopenai\b",
    "Gemini": r"\bgemini\b",
    "Hugging Face": r"\bhugging\s*face\b",
    "Transformers": r"\btransformers\b",
    "PyTorch": r"\bpytorch\b",
    "TensorFlow": r"\btensorflow\b",
    "Scikit-learn": r"\bscikit[\s-]*learn\b|\bsklearn\b",
    "Model Evaluation": r"\bmodel\s+evaluation\b",
}

# Signals showing actual implementation, not merely interest.
IMPLEMENTATION_PATTERN = re.compile(
    r"\b(built|developed|implemented|created|designed|"
    r"integrated|trained|fine.tuned|deployed|"
    r"constructed|engineered|implemented)\b",
    re.IGNORECASE
)

# Strong technical signals for practical AI systems.
STRONG_AI_SIGNALS = {
    "LangChain", "LangGraph", "LlamaIndex", "Google ADK",
    "RAG", "FAISS", "ChromaDB", "Vector Search",
    "Embeddings", "Tool Calling", "Multi-Agent",
    "Model Evaluation",
}


def extract_matched_ai_skills(text):
    """Find recognized AI technologies and concepts."""
    return [
        name
        for name, pattern in AI_PATTERNS.items()
        if re.search(pattern, text, re.IGNORECASE)
    ]


def split_evidence_blocks(text):
    """
    Group nearby resume lines so a technology can be
    evaluated together with its implementation context.
    """
    blocks = re.split(r"\n\s*\n", text)

    # Some PDF extractors produce no blank lines.
    if len(blocks) <= 1:
        lines = [line.strip() for line in text.splitlines()]
        blocks = [
            " ".join(lines[i:i + 4])
            for i in range(0, len(lines), 4)
        ]

    return [block.strip() for block in blocks if block.strip()]


def find_ai_evidence(text):
    """
    Find evidence of a practical AI implementation.
    Returns a short evidence snippet or None.
    """
    for block in split_evidence_blocks(text):
        matched = extract_matched_ai_skills(block)

        if not matched:
            continue

        has_implementation = bool(
            IMPLEMENTATION_PATTERN.search(block)
        )

        has_strong_signal = any(
            skill in STRONG_AI_SIGNALS for skill in matched
        )

        if has_implementation and has_strong_signal:
            return " ".join(block.split())[:350]

        # Model-specific implementation also counts.
        model_signals = {
            "PyTorch", "TensorFlow", "Scikit-learn",
            "Transformers", "Hugging Face",
            "OpenAI", "Gemini", "LLM"
        }

        if has_implementation and any(
            skill in model_signals for skill in matched
        ):
            return " ".join(block.split())[:350]

    return None


PYTHON_NEGATIVE_PATTERNS = [
    r"\binterested\s+in\s+(?:learning\s+)?python\b",
    r"\b(?:currently\s+)?learning\s+python\b",
    r"\b(?:want|planning|plan|hope)\s+to\s+learn\s+python\b",
    r"\bno\s+(?:experience|knowledge)\s+(?:in|with|of)\s+python\b",
]


def find_python_evidence(text):
    """Find positive Python experience in resume text."""
    snippets = re.split(r"[\n.!?]+", text)

    for snippet in snippets:
        snippet = snippet.strip()

        if not PYTHON_PATTERN.search(snippet):
            continue

        if any(
            re.search(pattern, snippet, re.IGNORECASE)
            for pattern in PYTHON_NEGATIVE_PATTERNS
        ):
            continue

        return snippet[:250]

    return None


def check_eligibility(candidate):
    """
    Determine candidate eligibility using resume evidence.
    """
    text = candidate.get("text") or ""

    python_evidence = find_python_evidence(text)
    has_python = bool(python_evidence)
    matched_ai = extract_matched_ai_skills(text)
    ai_evidence = find_ai_evidence(text)

    rejection_reasons = []

    if not has_python:
        rejection_reasons.append(
            "No evidence of Python stack"
        )

    if not ai_evidence:
        rejection_reasons.append(
            "No meaningful AI/agentic implementation evidence"
        )

    eligible = has_python and bool(ai_evidence)

    matched_skills = (
        (["Python"] if has_python else []) + matched_ai
    )

    return {
        "candidate_name": candidate.get("candidate_name"),
        "eligible": eligible,
        "rejection_reasons": rejection_reasons,
        "matched_skills": matched_skills,
        "evidence": {
        "python": python_evidence,
        "ai": ai_evidence,
        },
    }
