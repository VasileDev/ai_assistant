from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


# embed a single piece of text (used for the user's question)
def create_embedding(text: str):
    embedding = model.encode(text)
    return embedding


# embed all chunks at once, in batches
def embed_chunks(chunks: list[dict], batch_size: int = 32) -> list[dict]:

    # if the document has no text, return an empty list
    if len(chunks) == 0:
        return []

    # 1. collect the text of every chunk into a list
    texts = []
    for chunk in chunks:
        texts.append(chunk["text"])

    # 2. encode all texts at once (much faster than one by one)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 100 # idk why did claude added this
    )

    # 3. attach each embedding back to its chunk (same order)
    embedded_chunks = []
    for i in range(len(chunks)):
        embedded_chunks.append({
            "text": chunks[i]["text"],
            "page": chunks[i]["page"],
            "embedding": embeddings[i],
            "document_name": chunks[i]["document_name"]
        })

    return embedded_chunks