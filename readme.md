# AI Resume Screening & Ranking System

A Python-based CLI application that automatically screens, evaluates, and ranks resumes for an SDE internship requiring Python engineering skills and practical AI/LLM experience.

The system uses evidence-based eligibility filtering, explainable weighted scoring, and public GitHub activity to generate a ranked shortlist.

## 1. Overview

The application processes multiple PDF resumes in a single batch and performs the following operations:

1. Extracts resume text and candidate information.
2. Applies minimum eligibility requirements for Python and AI/agentic experience.
3. Evaluates eligible candidates using a weighted 100-point scoring model.
4. Enriches candidate scores using public GitHub activity.
5. Applies penalties for potentially shallow AI implementations.
6. Produces machine-readable JSON containing rankings, score breakdowns, evidence, and rejection reasons.

The system prioritizes explainability, reliability, and maintainability over interface complexity.

## 2. Technology Stack

- **Python 3:** Core implementation
- **PyMuPDF:** PDF text extraction
- **Requests:** GitHub REST API integration
- **python-dotenv:** Environment variable configuration
- **Pytest:** Automated testing
- **JSON:** Machine-readable results

## 3. Project Structure

```text
ai-resume-screener/
├── resumes/
│   └── candidate_*.pdf
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── eligibility.py
│   ├── scorer.py
│   └── github_service.py
├── tests/
│   ├── test_eligibility.py
│   ├── test_scorer.py
│   ├── test_github.py
│   └── test_pipeline.py
├── output/
│   └── results.json
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── readme.md
```

## 4. Setup Instructions

### Prerequisites

- Python 3.10+
- Git
- Internet access for GitHub enrichment

### Clone the Repository

```bash
git clone https://github.com/Aditya-Kandari-01/ai-resume-screening-system.git
cd ai-resume-screening-system
```

### Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure Environment Variables

Copy `.env.example` to `.env` and optionally provide a GitHub personal access token.

```dotenv
GITHUB_TOKEN=your_optional_token
GITHUB_TIMEOUT=5
```

A GitHub token is optional. Without one, GitHub API rate limits may restrict enrichment.

**Never commit API credentials.**

### Add Resume Dataset

Place the provided PDF resumes inside the `resumes/` directory.

## 5. Running the Application

### Full Screening With GitHub Enrichment

```bash
python main.py --input ./resumes --output ./output/results.json
```

### Offline Screening Without GitHub Requests

```bash
python main.py --input ./resumes --output ./output/results_offline.json --skip-github
```

Offline mode completes eligibility filtering and deterministic scoring but does not award GitHub points.

## 6. Screening Pipeline

```text
PDF Resume Directory
        |
        v
PDF Text Extraction
        |
        v
Candidate Information Extraction
        |
        v
Python + AI Eligibility Filtering
        |
        +---- Ineligible ---> Rejection Reasons
        |
        v
Weighted Candidate Scoring
        |
        v
GitHub Activity Enrichment
        |
        v
Project Quality Penalties
        |
        v
Candidate Ranking
        |
        v
results.json
```

## 7. Eligibility Filtering

Candidates must satisfy both minimum conditions.

### Python Evidence

The resume must demonstrate Python as a technical skill, project implementation language, or professional technology.

### AI / Agentic Evidence

The resume must demonstrate meaningful AI-related implementation, such as:

- Retrieval-Augmented Generation (RAG)
- LangChain or LangGraph
- Vector databases and embeddings
- AI agents and tool calling
- Machine learning or model development
- LLM-based applications with documented implementation

Eligibility is determined using deterministic regular expressions and contextual evidence heuristics.

Statements indicating only an interest in learning Python do not qualify as positive Python experience under the implemented rules.

Candidates who do not satisfy both conditions are rejected with explicit reasons.

## 8. Candidate Scoring Methodology

Eligible candidates are evaluated using a weighted scoring model.

| Category | Maximum Points |
|---|---:|
| AI / Agentic / RAG Project Depth | 40 |
| Python & Backend Engineering | 30 |
| Cloud / Deployment / Full Stack | 15 |
| GitHub Activity | 10 |
| Engineering Depth Signals | 5 |
| **Total** | **100** |

### AI Project Depth — 40 Points

Rewards evidence of practical AI implementation, retrieval/RAG systems, agentic orchestration, and advanced AI workflows such as evaluation or model training.

### Python & Backend Engineering — 30 Points

Evaluates Python evidence, frameworks such as FastAPI/Django/Flask, database technologies, and backend engineering signals.

### Cloud / Deployment / Full Stack — 15 Points

Rewards cloud infrastructure, containerization/deployment, and frontend technologies associated with full-stack development.

### GitHub Activity — 10 Points

Divided into:

- Up to 5 points for recent public activity.
- Up to 5 points for maintained and relevant public repositories.

### Engineering Depth — 5 Points

Rewards testing, reliability, architecture, performance optimization, and observability.

### Project Quality Penalties

An apparent thin LLM/API wrapper without evidence of deeper AI workflows may receive a 10-point deduction.

The penalty is recorded explicitly in the score output.

Scores are capped between 0 and 100.

## 9. GitHub Enrichment

The application uses the public GitHub REST API to retrieve profile, repository, and recent activity information.

The enrichment service:

- Extracts and validates GitHub usernames.
- Scores recent public activity.
- Identifies maintained and relevant repositories.
- Caches lookups during a screening run.
- Uses request timeouts.
- Handles missing profiles, HTTP 404 responses, rate limits, and network failures.

Missing or unavailable GitHub information never causes a candidate to fail eligibility.

Public GitHub information is a supplementary signal and may not represent all engineering activity, particularly private contributions.

## 10. Output Format

The application writes a JSON file containing:

- `summary`: Batch processing statistics.
- `ranked_candidates`: Eligible candidates sorted by final score.
- `rejected_candidates`: Ineligible candidates with rejection reasons.
- `failed_candidates`: Resumes that could not be processed successfully.

Each ranked candidate contains a score breakdown, matched skills, project summary, technical evidence, strengths, concerns, and GitHub enrichment information.

## 11. Testing

Run:

```bash
python -m pytest tests/ -v
```

The test suite covers eligibility rules, scoring limits, shallow AI project penalties, GitHub scoring, API failures, missing profiles, and batch pipeline behavior.

**Latest verified test result:** 20 tests passed.

## 12. Results on the Provided Dataset

The latest completed screening run produced:

| Metric | Result |
|---|---:|
| Total resumes | 50 |
| Successfully parsed | 50 |
| Eligible | 33 |
| Rejected | 17 |
| Failed | 0 |
| Successful GitHub enrichments | 12 |
| No detected GitHub profile | 20 |
| GitHub profile unavailable (404) | 1 |

These eligibility results are produced by the implemented rule-based model and have not been independently verified against manually labeled ground truth.

## 13. Design Decisions

### Deterministic Eligibility Filtering

Hard eligibility checks are rule-based to maintain predictability, explainability, and ease of testing.

### Explainable Weighted Scoring

Each score category contains identifiable technical signals and supporting evidence snippets. Scores are capped by category, and penalties are reported separately.

### LLM Usage

The current implementation does not call an external LLM for semantic evaluation.

Deterministic scoring was selected to maintain reliability and reproducibility within the assignment's time constraints.

While this approach is straightforward to test, it may miss semantically equivalent descriptions or incorrectly associate technical keywords with implementation evidence.

### GitHub Scoring

GitHub contributes a maximum of 10 points and is never an eligibility requirement.

Public activity and relevant repository information provide additional evidence but do not establish the full extent of a candidate's engineering capabilities.

### Fault Tolerance

Unreadable PDFs are recorded as failures without terminating the batch. GitHub API errors are handled separately from candidate eligibility.

### Modular Architecture

Parsing, eligibility evaluation, scoring, GitHub integration, and CLI orchestration are separated into dedicated modules for readability and maintainability.

## 14. Limitations

- PDF layouts can affect text and candidate-name extraction.
- Some candidate names may fall back to their source filenames.
- Rule-based filtering can generate false positives or false negatives.
- Scoring heuristics cannot fully assess architecture or implementation ownership.
- Keyword proximity is not equivalent to semantic understanding.
- Public GitHub activity may be incomplete.
- Scanned image-only PDFs may require OCR, which is not implemented.
- Duplicate-content detection is not currently implemented.

## 15. If I Had More Time

1. **Structured LLM Evaluation:** Add a Pydantic-validated LLM adapter to assess project depth and return evidence-backed judgments, while retaining deterministic eligibility and fallback scoring.
2. **Improved Resume Understanding:** Implement section-aware extraction, better candidate-name recognition, and OCR support for scanned resumes.
3. **Duplicate Detection and Caching:** Detect duplicate resumes using file hashes and persist GitHub enrichment results across runs.
4. **Ranking Validation:** Evaluate screening accuracy using manually reviewed examples and tune scoring thresholds to reduce false positives and false negatives.

## 16. Conclusion

This project demonstrates a modular, explainable approach to automated resume screening within a limited development time.

It combines PDF ingestion, rule-based eligibility evaluation, weighted engineering scoring, public GitHub enrichment, automated tests, and machine-readable ranking output.

The focus is on building a reliable system that another engineer can understand, run, test, and extend.
