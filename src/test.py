from ingestion.pipeline import ingest_document
from embeddings.embedding_model import embed_chunks
from embeddings.vector_store import (
    create_vector_store,
    search_vector_store
)


chunks = ingest_document(
    "../data/documents/About Dacia.pdf"
)

embedded_chunks = embed_chunks(chunks)

index = create_vector_store(embedded_chunks)

results = search_vector_store(
    "What is Dacia?",
    index,
    embedded_chunks
)

for result in results:
    print("Page:", result["page"])
    print(result["text"])
    print("---------------------")