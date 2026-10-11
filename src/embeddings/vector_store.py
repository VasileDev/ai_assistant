import faiss
import numpy as np
import json
import os

from embeddings.embedding_model import create_embedding

INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.json"

# the fields every saved chunk must have
CHUNK_FIELDS = ["text", "page", "document_name", "document_id"]


# build a FAISS index from the chunks that already have embeddings
def create_vector_store(embeded_chunks: list[dict]):
    # with no chunks there is nothing to index (ex: the PDFs had no text)
    if len(embeded_chunks) == 0:
        raise ValueError("No chunks to index. The documents contain no extractable text.")

    embeddings = [chunk["embedding"] for chunk in embeded_chunks] # create a new list with only the embeddings from the list with dicts

    embeddings = np.array(embeddings).astype("float32") # turn the list of embeddings into a numpy list

    # Normalize vectors so Inner Product ~= cosine similarity
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
    if top_k <= 0:
        raise ValueError("top_k must be a positive number.")

    # empty index -> nothing to find
    if index.ntotal == 0:
        return []

    # we can't ask FAISS for more results than there are vectors in the index
    top_k = min(top_k, index.ntotal)

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
            "document_id": chunk["document_id"],
            "score": score
        })

    return results


# check if a saved index already exists in the folder
def vector_store_exists(folder: str) -> bool:
    index_path = os.path.join(folder, INDEX_FILE)
    chunks_path = os.path.join(folder, CHUNKS_FILE)

    return os.path.exists(index_path) and os.path.exists(chunks_path)


# save the FAISS index and the chunks (without the vectors) to disk
def save_vector_store(index, embedded_chunks: list[dict], folder: str):
    # the index and the chunks must have the same size, otherwise they don't match anymore
    if index.ntotal != len(embedded_chunks):
        raise ValueError("The index and the chunks don't have the same number of entries.")

    # create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # 1. save the vectors
    faiss.write_index(index, os.path.join(folder, INDEX_FILE))

    # 2. save only the chunk fields (the vectors are already in the index)
    chunks_to_save = []
    for chunk in embedded_chunks:
        chunks_to_save.append({
            "text": chunk["text"],
            "page": chunk["page"],
            "document_name": chunk["document_name"],
            "document_id": chunk["document_id"]
        })

    with open(os.path.join(folder, CHUNKS_FILE), "w", encoding="utf-8") as f:
        json.dump(chunks_to_save, f, ensure_ascii=False, indent=2)


# load the FAISS index and the chunks from disk
# raises ValueError if the two files don't match (ex: an old index saved before document_id existed)
def load_vector_store(folder: str):
    index = faiss.read_index(os.path.join(folder, INDEX_FILE))

    with open(os.path.join(folder, CHUNKS_FILE), "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # every vector in the index must have exactly one chunk
    if index.ntotal != len(chunks):
        raise ValueError(
            f"The saved index has {index.ntotal} vectors but there are {len(chunks)} chunks."
        )

    # every saved chunk must have all the fields from CHUNK_FIELDS
    for chunk in chunks:
        for field in CHUNK_FIELDS:
            if field not in chunk:
                raise ValueError(
                    f"A saved chunk is missing the field '{field}'. Upload the documents again."
                )

    return index, chunks