# Chunking the pages extracted from the pdf 

def chunking_pages(
    pages: list[str],
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict]:


    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")
    elif not 0 <= overlap < chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than the chunk size."
        )

    chunks = []

    for page_number, page_text in enumerate(pages, start=1):
        page_text = " ".join(page_text.split()) # get rid of breaklines and other types of spaces, turning them into simple spaces
        start = 0

        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))

            if end < len(page_text):
                last_space = page_text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            chunk_text = page_text[start:end].strip()
            if chunk_text:
                chunks.append({"text": chunk_text, "page": page_number})

            if end == len(page_text):
                break

            # Move back for overlap, then start at the next word boundary.
            next_start = max(start + 1, end - overlap)
            while next_start < len(page_text) and page_text[next_start - 1] != " ":
                next_start += 1
            start = next_start

    return chunks