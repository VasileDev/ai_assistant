from ingestion.pipeline import ingest_documents
from embeddings.embedding_model import embed_chunks
from embeddings.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store,
    vector_store_exists
)
from rag.retriever import retrieve_context
from rag.rag_pipeline import answer_question

# !! outdated because now we need this list to contain dictionaries that have the path and also the name
DOCUMENT_NAMES = ["../data/documents/About Dacia.pdf", "../data/documents/Dacia Duster.pdf"]
INDEX_FOLDER = "../data/index"

if vector_store_exists(INDEX_FOLDER):
    print("Loading saved index...")
    index, embedded_chunks = load_vector_store(INDEX_FOLDER)
else:
    print("No saved index, building it...")
    chunks = ingest_documents(DOCUMENT_NAMES)
    embedded_chunks = embed_chunks(chunks)
    index = create_vector_store(embedded_chunks)
    save_vector_store(index, embedded_chunks, INDEX_FOLDER)
    print("Index saved.")

question = "In which document does dacia 1300 appear"

# results = retrieve_context(
#     question,
#     index,
#     embedded_chunks
# )

print(answer_question(question, index, embedded_chunks))
