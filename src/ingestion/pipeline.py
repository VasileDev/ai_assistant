# combines document_loader.py and text_splitter.py so only a call will be made, the 2 of them being complementary
from ingestion.document_loader import load_pdf
from ingestion.text_splitter import chunking_pages

def ingest_document(document_name: str) -> list[dict]:
    pages = load_pdf(document_name)

    chunks = chunking_pages(pages)

    return chunks