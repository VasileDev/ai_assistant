from ingestion.pipeline import ingest_documents

names = ["../data/documents/About Dacia.pdf", "../data/documents/Dacia Duster.pdf"]

chunks = ingest_documents(names)

for i, chunk in enumerate(chunks, start=1):
    print("------------------------------")
    print(f"{chunk['document_name']} | Pagina {chunk['page']}")
    print(f"[Continutul chunk-ului {i}]")