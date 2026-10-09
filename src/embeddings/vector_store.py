import faiss
import numpy as np
import json
import os

from embeddings.embedding_model import create_embedding

def create_vector_store(embeded_chunks: list[dict]):
    embeddings = [chunk["embedding"] for chunk in embeded_chunks] # create a new list with only the embeddings from the list with dicts

    embeddings = np.array(embeddings).astype("float32") # turn the list of embeddings into a numpy list

    # Normalize vectors so Inner Product ~= cosine similarity GPT SUGGESTION
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index

# return the chunks most similar to the user's question
def search_vector_store(
    query: str,
    index,
    embedded_chunks: list[dict],
    top_k: int = 3,
    min_score: float = 0.3
):
    query_embedding = create_embedding(query)

    query_embedding = np.array([query_embedding]).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for i in range(len(indices[0])):
        chunk_index = indices[0][i]
        score = float(scores[0][i])

        # FAISS returns -1 when it finds fewer results than top_k
        if chunk_index < 0:
            continue

        # skip chunks that are not similar enough to the question
        if score < min_score:
            continue

        chunk = embedded_chunks[chunk_index]

        results.append({
            "text": chunk["text"],
            "page": chunk["page"],
            "document_name": chunk["document_name"],
            "score": score
        })

    return results

INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.json"


# check if a saved index already exists in the folder
def vector_store_exists(folder: str) -> bool:
    index_path = os.path.join(folder, INDEX_FILE)
    chunks_path = os.path.join(folder, CHUNKS_FILE)

    return os.path.exists(index_path) and os.path.exists(chunks_path)


# save the FAISS index and the chunks (text + page) to disk
def save_vector_store(index, embedded_chunks: list[dict], folder: str):
    # create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # 1. save the vectors
    faiss.write_index(index, os.path.join(folder, INDEX_FILE))

    # 2. save only text, page and document_name (the vectors are already in the index)
    chunks_to_save = []
    for chunk in embedded_chunks:
        chunks_to_save.append({
            "text": chunk["text"],
            "page": chunk["page"],
            "document_name": chunk["document_name"]
        })

    with open(os.path.join(folder, CHUNKS_FILE), "w", encoding="utf-8") as f:
        json.dump(chunks_to_save, f, ensure_ascii=False, indent=2)

# load the FAISS index and the chunks from disk
def load_vector_store(folder: str):
    index = faiss.read_index(os.path.join(folder, INDEX_FILE))

    with open(os.path.join(folder, CHUNKS_FILE), "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return index, chunks