from fastapi import APIRouter, UploadFile
from pathlib import Path
from uuid import uuid4

from ingestion.pipeline import ingest_documents

# ai_assistant/src/api/ that's why is two
# parents[0]: api, parents[1]: src, parents[2]: ai_assistant 
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# folder where the pdfs will be stored
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

# creates the router object
router = APIRouter()

# eoot endpoint returning a greeting for now
@router.get("/")
async def root():
    return {"message": "hellow world"}

# document upload part
@router.post("/documents")
def upload_documents(files: list[UploadFile]) -> dict[str, int]:
    # files is a list with the object of the uploaded documents 

    # stores each saved file path and its original filename.
    document_identifiers = []

    # creates the folder where the copied versions of the uploaded pdfs will be saved if it doesn't exist 
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


    # goes around each pdf object uploaded
    for file in files:

        # generates a path for the future copied pdf 
        saved_path = UPLOAD_DIR / f"{uuid4().hex}.pdf"
        
        # get's the binary data of the uploaded pdf
        pdf_content = file.file.read()

        # creates the new pdfs on the path we created earlier
        with open(saved_path, "wb") as destination:
            destination.write(pdf_content)

        # adds dictionaries containing the path of each pdf and the original name of the pdf the user uploaded
        document_identifiers.append({
                "file_path": str(saved_path),
                "document_name": file.filename                
            }
        )

    chunks = ingest_documents(document_identifiers)

    for chunk in chunks:
        print(
            chunk["document_name"],
            chunk["page"],
            len(chunk["text"])
        )

    # testing purposes for now
    return {
        "documents_count": len(document_identifiers),
        "chunks_count": len(chunks)
    }



