from embeddings.vector_store import search_vector_store

# wrapper around search_vector_store() that returns the most relevant chunks for the question
def retrieve_context(
    question: str,
    index,
    embedded_chunks: list[dict],
    top_k: int = 3,
    min_score: float = 0.3
) -> list[dict]:
    """Retrieve the chunks that are most relevant to the question/prompt"""

    relevant_chunks = search_vector_store(
        query=question,
        index=index,
        embedded_chunks=embedded_chunks,
        top_k=top_k,
        min_score=min_score
    )

    return relevant_chunks