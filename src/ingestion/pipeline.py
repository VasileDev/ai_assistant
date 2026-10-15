from ingestion.document_loader import InvalidDocumentError, load_pdf
from ingestion.text_splitter import chunking_pages


def ingest_document(file_path: str, document_name: str, document_id: str) -> list[dict]:
    pages = load_pdf(file_path)
    chunks = chunking_pages(pages)
    if not chunks:
        raise InvalidDocumentError("The PDF has no extractable text.")

    for chunk in chunks:
        chunk["document_name"] = document_name
        chunk["document_id"] = document_id
    return chunks


def ingest_documents(document_identifiers: list[dict]) -> list[dict]:
    """Process the entire batch before the caller replaces the active index."""
    all_chunks = []
    for document in document_identifiers:
        try:
            chunks = ingest_document(
                document["file_path"],
                document["document_name"],
                document["document_id"],
            )
        except InvalidDocumentError as exc:
            raise InvalidDocumentError(f"{document['document_name']}: {exc}") from exc
        all_chunks.extend(chunks)
    return all_chunks
