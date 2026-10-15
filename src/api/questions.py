from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.store import get_store

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/questions")
def ask_question(body: QuestionRequest) -> dict:
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    # Keep one matching index/metadata snapshot for the whole request.
    store = get_store()
    if store is None:
        raise HTTPException(status_code=409, detail="Încarcă documente mai întâi")
    index, chunks = store

    # Delay model imports until needed. Task 4 supplies LLMError and the
    # structured answer; no API key is needed just to import this router.
    from rag.generator import LLMError
    from rag.rag_pipeline import answer_question

    try:
        return answer_question(question, index, chunks)
    except LLMError as exc:
        raise HTTPException(
            status_code=502,
            detail="The answer service is unavailable. Please try again.",
        ) from exc
