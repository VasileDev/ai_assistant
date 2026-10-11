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

            # True when the chunk ends on a space, False when a long word had to be cut in the middle
            cut_at_space = False

            # try to cut at the last space, so we don't split a word in two
            if end < len(page_text):
                last_space = page_text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space
                    cut_at_space = True

            chunk_text = page_text[start:end].strip()
            if chunk_text:
                chunks.append({"text": chunk_text, "page": page_number})

            if end == len(page_text):
                break

            # Move back for overlap
            next_start = max(start + 1, end - overlap)

            # Snap to the next word boundary ONLY if the chunk ended on a space.
            # If a long word (ex: an URL) was cut in the middle, snapping forward
            # would jump over the rest of that word and lose text (the old bug).
            if cut_at_space:
                while next_start < end and page_text[next_start - 1] != " ":
                    next_start += 1

            start = next_start

    return chunks