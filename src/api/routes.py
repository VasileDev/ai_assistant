import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from ingestion.document_loader import InvalidDocumentError
from ingestion.pipeline import ingest_documents
from services.store import rebuild_store

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
MAX_FILES = 10
MAX_FILE_BYTES = 20 * 1024 * 1024
COPY_BLOCK_BYTES = 1024 * 1024

logger = logging.getLogger(__name__)
router = APIRouter()


def _remove_failed_upload(paths: list[Path]) -> None:
    # These paths are created by this request, never supplied by the user.
    for path in paths:
        if path.resolve().parent != UPLOAD_DIR.resolve():
            logger.error("Refusing to delete a file outside the upload directory.")
            continue
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.exception("Could not remove a file from the failed upload.")


@router.post("/documents")
def upload_documents(files: list[UploadFile] = File(default=[])) -> dict:
    document_identifiers = []
    saved_paths = []

    try:
        if not 1 <= len(files) <= MAX_FILES:
            raise HTTPException(status_code=400, detail="Upload between 1 and 10 PDF files.")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        for file in files:
            # Preserve the original basename for citations, not for disk access.
            document_name = (file.filename or "").replace("\\", "/").rsplit("/", 1)[-1]
            if not document_name.strip():
                raise HTTPException(status_code=400, detail="Each file must have a filename.")
            document_id = uuid4().hex
            saved_path = UPLOAD_DIR / f"{document_id}.pdf"

            # Exclusive creation avoids overwriting even in the unlikely event
            # of a UUID collision. Copy in blocks instead of loading all bytes.
            size = 0
            with open(saved_path, "xb") as destination:
                saved_paths.append(saved_path)
                while block := file.file.read(COPY_BLOCK_BYTES):
                    size += len(block)
                    if size > MAX_FILE_BYTES:
                        raise HTTPException(
                            status_code=400,
                            detail=f"{document_name}: maximum file size is 20 MB (20 MiB).",
                        )
                    destination.write(block)
            if size == 0:
                raise HTTPException(status_code=400, detail=f"{document_name}: file is empty.")

            document_identifiers.append({
                "file_path": str(saved_path),
                "document_name": document_name,
                "document_id": document_id,
            })

        # No index changes happen until every PDF has passed ingestion.
        chunks = ingest_documents(document_identifiers)
        chunks_count = rebuild_store(chunks)
        return {
            "documents_count": len(document_identifiers),
            "chunks_count": chunks_count,
            "ready": True,
        }
    except HTTPException:
        _remove_failed_upload(saved_paths)
        raise
    except InvalidDocumentError as exc:
        _remove_failed_upload(saved_paths)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        _remove_failed_upload(saved_paths)
        logger.exception("Document upload or indexing failed.")
        raise HTTPException(status_code=500, detail="Documents could not be indexed. Please try again.") from exc
    finally:
        for file in files:
            try:
                file.file.close()
            except OSError:
                logger.warning("Could not close an uploaded file.", exc_info=True)
