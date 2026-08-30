# currently a testing ground
from ingestion.pipeline import ingest_document

chunks = ingest_document("../data/documents/About Dacia.pdf")

print(f"total chunks:{len(chunks)}")
print("_"*50)

for i, chunk in enumerate(chunks, start=1):
    print(f"Chunk: {i}")
    print(f"Page: {chunk['page']}")
    print(f"Length: {len(chunk['text'])} characters")
    print(f"Text: {chunk['text']}")
    print("_"*50)