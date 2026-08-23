from ingestion.document_loader import load_pdf
from ingestion.text_splitter import chunking_pages

pages = load_pdf("../data/documents/About Dacia.pdf")

chunks = chunking_pages(pages)

print("Pages:", len(pages))
print("Chunks:", len(chunks))

for chunk in chunks:
    print(chunk, "\n\n")