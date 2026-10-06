# knowledge-graph-rag-system — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does knowledge-graph-rag-system address, and what can you demonstrate?

Passages are triples written as sentences. Overlap retrieval cites the triple file.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/kgrag/main.py`](src/kgrag/main.py): Implementation or supporting configuration.
- [`src/kgrag/ops.py`](src/kgrag/ops.py): Implementation or supporting configuration.
- [`src/kgrag/answer.py`](src/kgrag/answer.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/kgrag/__init__.py`](src/kgrag/__init__.py): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `answer` and explain the decision it makes?

The main walkthrough here is `answer(question, source=None)` in [`src/kgrag/answer.py`](src/kgrag/answer.py#L16).

```python
def answer(question, source=None):
    if not isinstance(question, str) or not question.strip():
        raise InputError("question is empty")
    corpus = PASSAGES
    if source is not None:
        corpus = [item for item in corpus if item[0] == source]
        if not corpus:
            raise InputError(f"unknown source: {source}")
    query = words(question)
    ranked = []
    for name, text in corpus:
        overlap = query & words(text)
        ranked.append({"source": name, "text": text, "overlap": len(overlap)})
    ranked.sort(key=lambda row: (-row["overlap"], row["source"]))
    best = ranked[0]
    if best["overlap"] < MIN_OVERLAP:
        return {"answered": False, "answer": "No passage shares enough terms.", "citation": None, "passages": ranked}
    return {"answered": True, "answer": best["text"], "citation": best["source"], "passages": ranked}
```

The implementation calls `InputError`, `isinstance`, `len`, `question.strip`, `ranked.append`, `ranked.sort`, `words`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `words` have?

`words(text)` is defined in [`src/kgrag/answer.py`](src/kgrag/answer.py#L12).

Its return expressions include:

- `set(re.findall('[a-z0-9]+', text.lower())) - STOP`

It uses `re.findall`, `set`, `text.lower`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `InputError('question is empty')` in [`src/kgrag/answer.py`](src/kgrag/answer.py#L18).
- `InputError(f'unknown source: {source}')` in [`src/kgrag/answer.py`](src/kgrag/answer.py#L23).
- `HTTPException(status_code=422, detail=str(exc))` in [`src/kgrag/main.py`](src/kgrag/main.py#L19).
- `HTTPException(status_code=404, detail='workspace not found')` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_ask.py`](tests/test_ask.py#L7) contains `test_answers_and_refuses`:

```python
def test_answers_and_refuses():
    hit = client.post("/ask", json={"question": 'Which GKE cluster runs in europe-west1?'}).json()
    assert hit["answered"] is True
    assert hit["citation"] == "gke.md"
    miss = client.post("/ask", json={"question": 'football scores'}).json()
    assert miss["answered"] is False
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/kgrag/main.py`](src/kgrag/main.py#L10).
- `POST /ask` → `post_ask` in [`src/kgrag/main.py`](src/kgrag/main.py#L15).
- `GET /readyz` → `readyz` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L130).
- `POST /jobs/{job_id}/approve` → `approve_job` in [`src/kgrag/ops.py`](src/kgrag/ops.py#L140).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `STOP`, `PASSAGES` in [`src/kgrag/answer.py`](src/kgrag/answer.py); `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/kgrag/ops.py`](src/kgrag/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `answer`?

In [`src/kgrag/answer.py`](src/kgrag/answer.py#L16), `answer(question, source=None)` receives the inputs. The function computes these intermediate values:

- `corpus = PASSAGES`
- `query = words(question)`
- `ranked = []`
- `best = ranked[0]`

Its result is defined by:

- `{'answered': True, 'answer': best['text'], 'citation': best['source'], 'passages': ranked}`
- `{'answered': False, 'answer': 'No passage shares enough terms.', 'citation': None, 'passages': ranked}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/kgrag/answer.py`](src/kgrag/answer.py#L16) branches on:

- `not isinstance(question, str) or not question.strip()`
- `source is not None`
- `best['overlap'] < MIN_OVERLAP`
- `not corpus`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 14. What does the operations plane add, and where is its limit?

[`src/kgrag/ops.py`](src/kgrag/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
