# Chunking the pages extracted from the pdf 

def chunking_pages(
    pages: list[str],
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict]:

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.") # gpt suggestion
    chunks = []

    for page_number, page_text in enumerate(pages, start=1):
        page_text = page_text.strip()

        if not page_text:
            continue

        start = 0

        while start < len(page_text):
            end = start + chunk_size

            chunk_text = page_text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "page": page_number
                })

            if end >= len(page_text):
                break

            start = end - overlap

    return chunks