from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# embed a piece of text 
def create_embedding(text: str):
    embedding = model.encode(text)
    return embedding

# add the embedding part to the list of vectors with the text from the chunks and the page number
def embed_chunks(chunks: list[dict])->list[dict]:

    embedded_chunks = []

    for chunk in chunks: 

            embedding = create_embedding(chunk["text"])

            embedded_chunks.append({
                "text": chunk["text"],
                "page": chunk["page"],
                "embedding": embedding
            })

    return embedded_chunks