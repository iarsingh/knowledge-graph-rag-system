from kgrag.ops import router as ops_router
from fastapi import FastAPI, HTTPException
from kgrag.answer import InputError, answer

app = FastAPI()
app.include_router(ops_router, prefix="/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/ask")
def post_ask(body: dict):
    try:
        return answer(body.get("question"), body.get("source"))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
