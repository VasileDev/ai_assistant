from embeddings.embedding_model import create_embedding
from ingestion.pipeline import ingest_document

chunks = ingest_document("../data/documents/About Dacia.pdf")

for dic in chunks:
    print(create_embedding(dic["text"]))

