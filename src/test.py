from ingestion.pipeline import ingest_document
from embeddings.embedding_model import embed_chunks
from embeddings.vector_store import (
    create_vector_store,
    # search_vector_store
)
from rag.retriever import retrieve_context
from rag.generator import build_context, build_prompt, generate_answer
from rag.rag_pipeline import answer_question


chunks = ingest_document(
    "../data/documents/About Dacia.pdf"
)

embedded_chunks = embed_chunks(chunks)

index = create_vector_store(embedded_chunks)

question = "When was Dacia founded?"

results = retrieve_context(
    question,
    index,
    embedded_chunks
)

# results = search_vector_store(
#     "When was Dacia first created?",
#     index,
#     embedded_chunks
# )

# for result in results:
#     print("Page:", result["page"])
#     print(result["text"])
#     print("---------------------")


# prompt = build_prompt(question, results)
# print(prompt)

# answer = generate_answer(question, results)
# print(answer)

print(answer_question(question, index, embedded_chunks))
