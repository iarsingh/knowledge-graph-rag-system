import re

STOP = {"the", "a", "an", "is", "of", "and", "to", "in", "what", "why", "does", "how"}
PASSAGES = [("gke.md", 'GKE cluster platform-prod runs in europe-west1.'), ("rel.md", 'platform-prod uses the shared vpc host-net.')]
MIN_OVERLAP = 2


class InputError(ValueError):
    pass


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOP


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
