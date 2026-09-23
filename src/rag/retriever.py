from embeddings.vector_store import search_vector_store

# wrapper around search_vector_store() from embeddings.vector_store
def retrieve_content(
    question: str,
    index,
    embedded_chunks: list[dict],
    top_k: int=3 
)->list[dict]:
    """Retrieve the chunk that are most relevant to the question/prompt"""

    relevant_chunks = search_vector_store(
        query=question,
        index=index,
        embedded_chunks=embedded_chunks,
        top_k=top_k
    )

    return relevant_chunks