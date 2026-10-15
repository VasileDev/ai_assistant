def chunking_pages(
    pages: list[str],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """Split page text into chunks while retaining physical page numbers."""
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")
    if not 0 <= overlap < chunk_size:
        raise ValueError("Overlap must be non-negative and smaller than chunk size.")

    chunks = []
    for page_number, raw_text in enumerate(pages, start=1):
        page_text = " ".join(raw_text.split())
        start = 0
        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))
            cut_at_space = False

            if end < len(page_text):
                last_space = page_text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space
                    cut_at_space = True

            text = page_text[start:end].strip()
            if text:
                chunks.append({"text": text, "page": page_number})
            if end == len(page_text):
                break

            next_start = max(start + 1, end - overlap)
            # Do not skip the rest of a long word or URL split at chunk_size.
            if cut_at_space:
                while next_start < end and page_text[next_start - 1] != " ":
                    next_start += 1
            start = next_start

    return chunks
