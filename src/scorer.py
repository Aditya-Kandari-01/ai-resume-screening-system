
import re

from src.eligibility import check_eligibility


# Category weights required by the assignment.
WEIGHTS = {
    "ai_project_depth": 40,
    "python_backend": 30,
    "cloud_fullstack": 15,
    "github": 10,
    "engineering_depth": 5,
}


def find_evidence(text, patterns):
    """
    Find a matching technical signal and return
    a short evidence snippet from the resume.
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            start = max(0, match.start() - 90)
            end = min(len(text), match.end() + 130)

            return " ".join(text[start:end].split())

    return None


def score_ai(text, ai_evidence):
    """
    Score AI project depth out of 40.
    Technical implementation evidence is required.
    """
    score = 0
    evidence = []

    if not ai_evidence:
        return 0, evidence

    # 10: Practical implementation
    score += 10
    evidence.append("AI implementation: " + ai_evidence[:180])

    # 10: Retrieval / RAG implementation
    retrieval = find_evidence(text, [
        r"\bretrieval.augmented generation\b",
        r"\brag\s+(?:pipeline|system|application|chatbot)\b",
        r"\b(?:faiss|chromadb)\b",
        r"\bvector\s+(?:search|database|db)\b",
        r"\bsemantic\s+search\b",
    ])

    if retrieval and re.search(
        r"\b(built|developed|implemented|designed|"
        r"integrated|engineered|created|trained)\b",
        retrieval,
        re.IGNORECASE
    ):
        score += 10
        evidence.append("Retrieval/RAG: " + retrieval)

    # 10: Agentic orchestration
    agents = find_evidence(text, [
        r"\blanggraph\b",
        r"\bmulti[\s-]agent\b",
        r"\btool[\s-]+calling\b",
        r"\bagent\s+(?:orchestration|workflow|state)\b",
        r"\bstateful\s+agent\b",
    ])

    if agents and re.search(
    r"\b(built|developed|implemented|designed|"
    r"integrated|engineered|created|trained)\b",
    agents,
    re.IGNORECASE
    ):
        score += 10
        evidence.append("Agentic workflow: " + agents)

    # 10: Evaluation, training or deeper workflows
    advanced = find_evidence(text, [
        r"\bmodel\s+evaluation\b",
        r"\b(?:fine[\s-]?tuned|fine[\s-]?tuning)\b",
        r"\b(?:trained|training)\s+(?:an?\s+)?(?:ml|ai|neural|machine.learning|classification)\b",
        r"\b(?:precision|recall|f1[\s-]?score)\b",
        r"\b(?:chunking|reranking|re-ranking)\b",
        r"\b(?:model|pipeline)\s+(?:monitoring|validation)\b",
    ])

    if advanced:
        score += 10
        evidence.append("Advanced AI implementation: " + advanced)

    return min(score, 40), evidence


def score_python_backend(text, python_evidence):
    """Score Python/backend capability out of 30."""
    score = 0
    evidence = []

    if python_evidence:
        score += 10
        evidence.append("Python: " + python_evidence[:180])

    frameworks = find_evidence(text, [
        r"\bfastapi\b",
        r"\bdjango\b",
        r"\bflask\b",
    ])

    if frameworks:
        score += 8
        evidence.append("Backend framework: " + frameworks)

    databases = find_evidence(text, [
        r"\bpostgresql\b",
        r"\bpostgres\b",
        r"\bredis\b",
        r"\bsqlalchemy\b",
        r"\bmongodb\b",
        r"\bmysql\b",
    ])

    if databases:
        score += 6
        evidence.append("Data layer: " + databases)

    backend = find_evidence(text, [
        r"\basync(?:io)?\b",
        r"\basynchronous\b",
        r"\brest(?:ful)?\s+api\b",
        r"\bapi\s+(?:development|integration|design)\b",
        r"\bbackground\s+(?:tasks|jobs|workers)\b",
        r"\bmicroservices?\b",
    ])

    if backend:
        score += 6
        evidence.append("Backend engineering: " + backend)

    return min(score, 30), evidence


def score_cloud_fullstack(text):
    """Score deployment and full-stack signals out of 15."""
    score = 0
    evidence = []

    cloud = find_evidence(text, [
        r"\bgcp\b",
        r"\bgoogle\s+cloud\b",
        r"\baws\b",
        r"\bazure\b",
        r"\bcloud\s+run\b",
    ])

    if cloud:
        score += 5
        evidence.append("Cloud: " + cloud)

    deployment = find_evidence(text, [
        r"\bdocker\b",
        r"\bkubernetes\b",
        r"\bci/cd\b",
        r"\bgithub\s+actions\b",
        r"\bdeployed\b",
        r"\bdeployment\b",
    ])

    if deployment:
        score += 5
        evidence.append("Deployment: " + deployment)

    frontend = find_evidence(text, [
        r"\breact(?:js|\.js)?\b",
        r"\bnext(?:js|\.js)?\b",
        r"\bfull[\s-]stack\b",
    ])

    if frontend:
        score += 5
        evidence.append("Full-stack: " + frontend)

    return min(score, 15), evidence


def score_engineering_depth(text):
    """Score engineering practices out of 5."""
    signals = [
        ("Testing", [
            r"\bunit\s+test",
            r"\bpytest\b",
            r"\bjunit\b",
        ]),
        ("Reliability", [
            r"\berror\s+handling\b",
            r"\bretry\s+logic\b",
            r"\bfault[\s-]+toleran",
        ]),
        ("Architecture", [
            r"\bsystem\s+design\b",
            r"\bdesign\s+patterns\b",
            r"\bevent[\s-]+driven\b",
        ]),
        ("Performance", [
            r"\bcach(?:e|ing)\b",
            r"\bconcurren",
            r"\bload\s+balanc",
        ]),
        ("Observability", [
            r"\bmonitoring\b",
            r"\blogging\b",
            r"\btracing\b",
            r"\bmetrics\b",
        ]),
    ]

    evidence = []

    for label, patterns in signals:
        snippet = find_evidence(text, patterns)

        if snippet:
            evidence.append(f"{label}: {snippet}")

    return min(len(evidence), 5), evidence


def calculate_ai_penalty(text, ai_evidence):
    """
    Apply a 5–15 point penalty to apparent thin
    LLM/API wrappers without deeper AI workflows.
    """
    if not ai_evidence:
        return 0, None

    wrapper = find_evidence(text, [
        r"\b(?:openai|gemini|llm)\s+api\b",
        r"\bapi\s+(?:call|calls)\b",
        r"\bprompt\s+engineering\b",
    ])

    if not wrapper:
        return 0, None

    deep_workflow = find_evidence(text, [
        r"\brag\b",
        r"\bretrieval\b",
        r"\bembeddings?\b",
        r"\bvector\s+(?:search|db|database)\b",
        r"\blanggraph\b",
        r"\bmulti[\s-]agent\b",
        r"\btool[\s-]+calling\b",
        r"\bfine[\s-]?tun",
        r"\bmodel\s+evaluation\b",
    ])

    if deep_workflow:
        return 0, None

    return 10, (
        "Potential thin LLM/API wrapper: no deeper "
        "retrieval, agentic or evaluation evidence found."
    )


def score_candidate(candidate, eligibility=None, github_score=0):
    """
    Score an eligible candidate.

    github_score is supplied by the GitHub
    enrichment module in Step 4.
    """
    if eligibility is None:
        eligibility = check_eligibility(candidate)

    if not eligibility["eligible"]:
        raise ValueError("Cannot score an ineligible candidate")

    text = candidate.get("text") or ""

    python_evidence = eligibility["evidence"]["python"]
    ai_evidence = eligibility["evidence"]["ai"]

    ai_score, ai_details = score_ai(text, ai_evidence)
    python_score, python_details = score_python_backend(
        text, python_evidence
    )
    cloud_score, cloud_details = score_cloud_fullstack(text)
    engineering_score, engineering_details = (
        score_engineering_depth(text)
    )

    github_score = max(0, min(10, int(github_score)))

    breakdown = {
        "ai_project_depth": ai_score,
        "python_backend": python_score,
        "cloud_fullstack": cloud_score,
        "github": github_score,
        "engineering_depth": engineering_score,
    }

    penalty, penalty_reason = calculate_ai_penalty(
        text, ai_evidence
    )

    raw_score = sum(breakdown.values())
    total_score = max(0, min(100, raw_score - penalty))

    evidence = {
        "ai_project_depth": ai_details,
        "python_backend": python_details,
        "cloud_fullstack": cloud_details,
        "engineering_depth": engineering_details,
    }

    strengths = []

    if ai_score >= 30:
        strengths.append("Strong AI project depth")
    elif ai_score >= 20:
        strengths.append("Practical AI implementation")

    if python_score >= 24:
        strengths.append("Strong Python/backend evidence")

    if cloud_score >= 10:
        strengths.append("Cloud and deployment exposure")

    if engineering_score >= 3:
        strengths.append("Engineering maturity signals")

    concerns = []

    if ai_score <= 10:
        concerns.append("Limited advanced AI workflow evidence")

    if python_score < 18:
        concerns.append("Limited demonstrated backend depth")

    if penalty_reason:
        concerns.append(penalty_reason)

    return {
        "candidate_name": candidate.get("candidate_name"),
        "eligible": True,
        "total_score": total_score,
        "score_breakdown": breakdown,
        "penalty": penalty,
        "matched_skills": eligibility["matched_skills"],
        "project_summary": ai_evidence[:350] if ai_evidence else "",
        "evidence": evidence,
        "strengths": strengths,
        "concerns": concerns,
    }
