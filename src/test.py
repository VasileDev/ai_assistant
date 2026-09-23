from ingestion.pipeline import ingest_document
from embeddings.embedding_model import embed_chunks
from embeddings.vector_store import (
    create_vector_store,
    # search_vector_store
)
from rag.retriever import retrieve_content


chunks = ingest_document(
    "../data/documents/About Dacia.pdf"
)

embedded_chunks = embed_chunks(chunks)

index = create_vector_store(embedded_chunks)

results = retrieve_content(
    "When was Dacia founded?",
    index,
    embedded_chunks
)

# results = search_vector_store(
#     "When was Dacia first created?",
#     index,
#     embedded_chunks
# )

for result in results:
    print("Page:", result["page"])
    print(result["text"])
    print("---------------------")