from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "hellow world"}
    
@router.post("/documents")
def upload_documents(files: list[UploadFile]):
    filenames = []

    for file in files:
        filenames.append(file.filename)

    return {"filenames": filenames}

