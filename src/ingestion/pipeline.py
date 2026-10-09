# combines document_loader.py and text_splitter.py so only a call will be made, the 2 of them being complementary
from ingestion.document_loader import load_pdf
from ingestion.text_splitter import chunking_pages

def ingest_document(document_name: str) -> list[dict]:
    pages = load_pdf(document_name) # list containing each page of the document

    chunks = chunking_pages(pages) # a list of dicttionaires that contain the chunk and the page number of that chunk

    for chunk in chunks:
        chunk["document_name"] = document_name

    return chunks

# puts all the pdfs ingested in the same list for easier later use
def ingest_documents(document_names: list[str]) -> list[dict]:

    # future list with all the chunks of all the documents uploaded
    all_chunks = []

    # goes around the list of documet names
    for document in document_names:
        
        #creates a lsit of dictionaries containing only one's document name, page number and chunk of one document 
        chunks = ingest_document(document)
        
        # goes around all the chunks and adds them into the complete list
        for chunk in chunks:
            all_chunks.append(chunk)

    return all_chunks