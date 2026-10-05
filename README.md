# Knowledge Graph + RAG System

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/kgrag/main.py`](src/kgrag/main.py) | HTTP handlers: `GET /healthz`, `POST /ask` |
| [`src/kgrag/answer.py`](src/kgrag/answer.py) | Functions: `words`, `answer` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/kgrag/__init__.py`](src/kgrag/__init__.py) | Implementation or supporting configuration |
| [`tests/test_ask.py`](tests/test_ask.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn kgrag.main:app --reload
```

<!-- project-guide:end -->

Level: 7 — Intermediate & Advanced RAG

Skills: Python, subject-relation sentences

Passages are triples written as sentences. Overlap retrieval cites the triple file.

```bash
pip install -r requirements.txt
pytest -q
```

This is a local laptop proof. It does not call a hosted model and it does not apply production changes.

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
