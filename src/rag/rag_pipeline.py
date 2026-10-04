from rag.retriever import retrieve_context
from rag.generator import generate_answer

NO_ANSWER_MESSAGE = "I could not find the answer in the provided document."


def answer_question(
    question: str,
    index,
    embedded_chunks: list[dict],
    top_k: int = 3,
    min_score: float = 0.3
) -> str:
    retrieved_chunks = retrieve_context(
        question=question,
        index=index,
        embedded_chunks=embedded_chunks,
        top_k=top_k,
        min_score=min_score
    )

    # no relevant chunk found -> don't call the LLM at all
    if len(retrieved_chunks) == 0:
        return NO_ANSWER_MESSAGE

    answer = generate_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    return answer