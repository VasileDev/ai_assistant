import faiss
import numpy as np

from embeddings.embedding_model import create_embedding

def create_vector_store(embeded_chunks: list[dict]):
    embeddings = [chunk["embedding"] for chunk in embeded_chunks] 

    embeddings = np.array(embeddings).astype("float32")

    # Normalize vectors so Inner Product ~= cosine similarity GPT SUGGESTION
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index

# return similar chunks to the user's prompt
def search_vector_store(
    query: str,
    index,
    embedded_chunks: list[dict],
    top_k: int=3 
):
    query_embedding = create_embedding(query)

    query_embedding = np.array([query_embedding]).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for i in indices[0]:
        if i >= 0:
            results.append(embedded_chunks[i])

    return results