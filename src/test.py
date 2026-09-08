from embeddings.embedding_model import embed_chunks
from ingestion.pipeline import ingest_document

chunks = ingest_document("../data/documents/About Dacia.pdf")

print(embed_chunks(chunks[:1]))

