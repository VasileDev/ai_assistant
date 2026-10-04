from ingestion.document_loader import load_pdf

from ingestion.pipeline import ingest_document

pdf_name = "../data/documents/About Dacia.pdf"

chunks = ingest_document(pdf_name)

for text in chunks:
    print("------------------------------\n\n", text, "------------------------------\n\n")