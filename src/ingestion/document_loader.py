from pypdf import PdfReader


class InvalidDocumentError(ValueError):
    """The uploaded file cannot be used as a readable PDF."""


def load_pdf(pdf_name: str) -> list[str]:
    """Read physical pages in order; preserve empty pages for correct numbering."""
    # Opening errors are server/storage errors, not necessarily invalid PDFs.
    with open(pdf_name, "rb") as source:
        try:
            reader = PdfReader(source)
            if reader.is_encrypted:
                raise InvalidDocumentError("Password-protected PDFs are not supported.")
            pages = [page.extract_text() or "" for page in reader.pages]
        except InvalidDocumentError:
            raise
        except Exception as exc:
            # Parser errors must not expose internal file paths to the client.
            raise InvalidDocumentError("The file is not a readable PDF.") from exc

    if not any(page.strip() for page in pages):
        raise InvalidDocumentError("The PDF has no extractable text. Scanned PDFs need OCR.")
    return pages
