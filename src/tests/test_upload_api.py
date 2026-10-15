from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import routes


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(routes.router)
    return TestClient(app)


def test_upload_returns_counts_and_keeps_original_names(monkeypatch):
    upload_dir = Path(__file__).resolve().parent
    saved_documents = []
    monkeypatch.setattr(routes, "UPLOAD_DIR", upload_dir)

    def fake_ingest(documents):
        assert len(documents) == 2
        assert [document["document_name"] for document in documents] == ["Manual.pdf", "Guide.pdf"]
        assert all(Path(document["file_path"]).is_file() for document in documents)
        saved_documents.extend(Path(document["file_path"]) for document in documents)
        return [{"text": "chunk"}, {"text": "another chunk"}]

    monkeypatch.setattr(routes, "ingest_documents", fake_ingest)
    monkeypatch.setattr(routes, "rebuild_store", lambda chunks: len(chunks))

    with make_client() as client:
        response = client.post(
            "/documents",
            files=[
                ("files", ("folder\\Manual.pdf", b"pdf one", "application/pdf")),
                ("files", ("Guide.pdf", b"pdf two", "application/pdf")),
            ],
        )

    assert response.status_code == 200
    assert response.json() == {"documents_count": 2, "chunks_count": 2, "ready": True}
    for path in saved_documents:
        path.unlink(missing_ok=True)


def test_failed_ingestion_removes_new_uploads_and_returns_bad_request(monkeypatch):
    upload_dir = Path(__file__).resolve().parent
    existing_files = set(upload_dir.glob("*.pdf"))
    monkeypatch.setattr(routes, "UPLOAD_DIR", upload_dir)

    def reject_documents(_documents):
        raise routes.InvalidDocumentError("The file is not a readable PDF.")

    monkeypatch.setattr(routes, "ingest_documents", reject_documents)

    with make_client() as client:
        response = client.post(
            "/documents",
            files=[("files", ("bad.pdf", b"not a pdf", "application/pdf"))],
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "The file is not a readable PDF."
    assert set(upload_dir.glob("*.pdf")) == existing_files
