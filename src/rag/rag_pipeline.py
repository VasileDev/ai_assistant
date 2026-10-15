from rag.retriever import retrieve_context
from rag.generator import generate_answer, LLMError  # LLMError is imported here so the API can use it from this file

NO_ANSWER_MESSAGE = "I could not find the answer in the provided document."


# turn the retrieved chunks into the sources shown in the interface
def build_sources(retrieved_chunks: list[dict]) -> list[dict]:
    sources = []
    for chunk in retrieved_chunks:
        sources.append({
            "document_name": chunk["document_name"],
            "document_id": chunk["document_id"],
            "page": chunk["page"],
            "score": round(chunk["score"], 3),  # similarity, NOT the probability that the answer is correct
            "text": chunk["text"]
        })
    return sources


# returns {"answer": str, "sources": [...]}
# "sources" are the chunks that were found and given to the LLM
# (not all of them were necessarily used in the answer)
# raises LLMError if the LLM can't be reached
def answer_question(
    question: str,
    index,
    embedded_chunks: list[dict],
    top_k: int = 3,
    min_score: float = 0.3
) -> dict:
    retrieved_chunks = retrieve_context(
        question=question,
        index=index,
        embedded_chunks=embedded_chunks,
        top_k=top_k,
        min_score=min_score
    )

    # no relevant chunk found -> don't call the LLM at all
    if len(retrieved_chunks) == 0:
        return {"answer": NO_ANSWER_MESSAGE, "sources": []}

    answer = generate_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    # the LLM says it couldn't find the answer -> don't show sources it didn't use
    if NO_ANSWER_MESSAGE in answer:
        return {"answer": NO_ANSWER_MESSAGE, "sources": []}

    return {
        "answer": answer,
        "sources": build_sources(retrieved_chunks)
    }