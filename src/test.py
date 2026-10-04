from ingestion.pipeline import ingest_document
from embeddings.embedding_model import embed_chunks
from embeddings.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store,
    vector_store_exists
)
from rag.retriever import retrieve_context
from rag.rag_pipeline import answer_question


PDF_PATH = "../data/documents/About Dacia.pdf"
INDEX_FOLDER = "../data/index"

if vector_store_exists(INDEX_FOLDER):
    print("Loading saved index...")
    index, embedded_chunks = load_vector_store(INDEX_FOLDER)
else:
    print("No saved index, building it...")
    chunks = ingest_document(PDF_PATH)
    embedded_chunks = embed_chunks(chunks)
    index = create_vector_store(embedded_chunks)
    save_vector_store(index, embedded_chunks, INDEX_FOLDER)
    print("Index saved.")

question = "Tell me a Dacia model"

# results = retrieve_context(
#     question,
#     index,
#     embedded_chunks
# )


questions = [
    "Tell me a Dacia model",
    "When was Dacia founded?",
    "What is the capital of France?",
    "How do I cook pasta?"
]

for q in questions:
    chunks_found = retrieve_context(q, index, embedded_chunks, min_score=0.0)
    print(q)
    for c in chunks_found:
        print(f"   page {c['page']}  score {c['score']:.3f}")
    print()

print(answer_question(questions[0], index, embedded_chunks))
