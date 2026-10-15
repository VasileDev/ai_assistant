"""One active index for a single server process (not multiple Uvicorn workers)."""

import logging
import os
import shutil
from pathlib import Path
from threading import Lock

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = PROJECT_ROOT / "data" / "index"
TEMP_DIR = PROJECT_ROOT / "data" / "index_tmp"
BUILD_DIR = TEMP_DIR / "new"
BACKUP_DIR = TEMP_DIR / "previous"

logger = logging.getLogger(__name__)
_store: tuple | None = None
_state_lock = Lock()
_rebuild_lock = Lock()
_REQUIRED_FIELDS = {"text", "page", "document_name", "document_id"}


def get_store() -> tuple | None:
    """Return (index, chunks), or None. Callers must treat this snapshot as read-only."""
    with _state_lock:
        return _store


def _validate_chunks(chunks: list[dict]) -> None:
    if not chunks:
        raise ValueError("Cannot build or load an index without readable chunks.")
    for chunk in chunks:
        if not isinstance(chunk, dict) or not _REQUIRED_FIELDS.issubset(chunk):
            raise ValueError("Chunk source metadata is missing. Rebuild the index.")
        for field in ("text", "document_name", "document_id"):
            if not isinstance(chunk[field], str) or not chunk[field].strip():
                raise ValueError(f"Chunk field '{field}' must be a non-empty string.")
        if type(chunk["page"]) is not int or chunk["page"] < 1:
            raise ValueError("Chunk page must be a positive integer.")


def _read_store(folder: Path) -> tuple:
    # Import on use: importing this service alone does not load the model.
    from embeddings.vector_store import load_vector_store

    index, chunks = load_vector_store(str(folder))
    _validate_chunks(chunks)
    if index.ntotal != len(chunks):
        raise ValueError("The index and chunk metadata have different sizes.")
    return index, chunks


def _remove_temporary_folder(folder: Path) -> None:
    # Only delete service-owned folders inside data/index_tmp.
    resolved = folder.resolve()
    if resolved == TEMP_DIR.resolve() or not resolved.is_relative_to(TEMP_DIR.resolve()):
        raise ValueError("Refusing to remove a folder outside the temporary directory.")
    if folder.exists():
        shutil.rmtree(folder)


def _recover_interrupted_swap() -> None:
    # Recover if the process stopped between the two directory renames.
    if not INDEX_DIR.exists() and BACKUP_DIR.exists():
        os.replace(BACKUP_DIR, INDEX_DIR)


def rebuild_store(chunks: list[dict]) -> int:
    """Prepare a replacement on disk before publishing it in memory."""
    global _store

    # Only one writer uses the staging directory at a time. Readers can keep
    # using the old snapshot while embeddings and disk writes are in progress.
    with _rebuild_lock:
        _validate_chunks(chunks)
        source_chunks = [dict(chunk) for chunk in chunks]
        from embeddings.embedding_model import embed_chunks
        from embeddings.vector_store import create_vector_store, save_vector_store

        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        _recover_interrupted_swap()
        _remove_temporary_folder(BUILD_DIR)
        _remove_temporary_folder(BACKUP_DIR)

        try:
            embedded_chunks = embed_chunks(source_chunks)
            index = create_vector_store(embedded_chunks)
            if index.ntotal != len(source_chunks):
                raise ValueError("Indexing did not preserve the number of chunks.")
            save_vector_store(index, embedded_chunks, str(BUILD_DIR))

            # Reload to check the saved files and preserve the same metadata
            # representation before and after a server restart.
            new_store = _read_store(BUILD_DIR)
            expected = [
                {key: value for key, value in chunk.items() if key != "embedding"}
                for chunk in source_chunks
            ]
            if new_store[1] != expected:
                raise ValueError("Saving changed or dropped chunk metadata.")

            # Non-empty directories cannot be replaced directly on every OS.
            # Keep a backup and restore it if promoting the new folder fails.
            with _state_lock:
                had_previous = INDEX_DIR.exists()
                if had_previous:
                    os.replace(INDEX_DIR, BACKUP_DIR)
                try:
                    os.replace(BUILD_DIR, INDEX_DIR)
                except Exception:
                    if had_previous:
                        os.replace(BACKUP_DIR, INDEX_DIR)
                    raise
                _store = new_store
        except Exception:
            try:
                _remove_temporary_folder(BUILD_DIR)
            except OSError:
                logger.warning("Could not clean the failed index build.", exc_info=True)
            raise

        # Once committed, a cleanup failure must not report the upload as failed.
        try:
            _remove_temporary_folder(BACKUP_DIR)
        except OSError:
            logger.warning("Index saved, but its backup could not be removed.", exc_info=True)
        return len(new_store[1])


def load_store_on_startup() -> None:
    """Load saved data, or log the error and start without documents if corrupt."""
    global _store

    with _rebuild_lock:
        loaded = None
        try:
            _recover_interrupted_swap()
            if INDEX_DIR.exists():
                loaded = _read_store(INDEX_DIR)
        except Exception:
            logger.exception("Could not load the saved index. Starting without documents.")
        with _state_lock:
            _store = loaded
