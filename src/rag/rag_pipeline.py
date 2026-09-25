from rag.retriever import retrieve_context
from rag.generator import generate_answer

def answer_question(
    question: str,
    index,
    embedded_chunks: list[dict],
    top_k: int=3
)->str:
    retrieved_chunks = retrieve_context(
        question=question,
        index=index,
        embedded_chunks=embedded_chunks,
        top_k=top_k
    )

    answer = generate_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    return answer