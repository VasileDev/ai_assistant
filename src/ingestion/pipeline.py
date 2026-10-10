# combines document_loader.py and text_splitter.py so only a call will be made, the 2 of them being complementary
from ingestion.document_loader import load_pdf
from ingestion.text_splitter import chunking_pages

def ingest_document(file_path: str, document_name: str) -> list[dict]:
    pages = load_pdf(file_path) # list containing each page of the document

    chunks = chunking_pages(pages) # a list of dicttionaires that contain the chunk and the page number of that chunk

    for chunk in chunks:
        chunk["document_name"] = document_name

    return chunks 

# puts all the pdfs ingested in the same list for easier later use
# document_identifiers is a list that contains dictionaries for each document
# those dictionaries have the path and the name of the document
# example: document_identifiers = [{"file_path": "data/uploads/document_name", "document_name": "document_name"}]
def ingest_documents(document_identifiers: list[dict]) -> list[dict]: 

    # future list with all the chunks of all the documents uploaded
    all_chunks = []

    # goes around the list of documet names
    for document in document_identifiers:
        
        #creates a lsit of dictionaries containing only one's name, page number and chunk of one document 
        chunks = ingest_document(
            document["file_path"],
            document["document_name"]
        )
        
        # goes around all the chunks and adds them into the complete list
        for chunk in chunks:
            all_chunks.append(chunk)

    return all_chunks