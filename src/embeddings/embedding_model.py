from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embedding(text: str)->list[dict]:
    embedding = model.encode(text)
    return embedding

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