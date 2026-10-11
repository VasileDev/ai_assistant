import json
import os

import numpy as np
import pytest

from embeddings import vector_store
from embeddings.vector_store import (
    CHUNKS_FILE,
    create_vector_store,
    load_vector_store,
    save_vector_store,
    search_vector_store,
)

# small fake vectors instead of the real model, so the tests are fast and predictable
FAKE_VECTORS = {
    "cats": [1.0, 0.0, 0.0],
    "dogs": [0.0, 1.0, 0.0],
    "cars": [0.0, 0.0, 1.0],
}


# 3 chunks from 2 documents with the SAME name but different ids
def make_chunks():
    return [
        {"text": "text about cats", "page": 1, "document_name": "same_name.pdf",
         "document_id": "id-0", "embedding": np.array(FAKE_VECTORS["cats"])},
        {"text": "text about dogs", "page": 2, "document_name": "same_name.pdf",
         "document_id": "id-1", "embedding": np.array(FAKE_VECTORS["dogs"])},
        {"text": "text about cars", "page": 3, "document_name": "same_name.pdf",
         "document_id": "id-2", "embedding": np.array(FAKE_VECTORS["cars"])},
    ]


# runs before every test: the question "dogs" gets the "dogs" vector, and so on
# (monkeypatch replaces the real create_embedding only during the test)
@pytest.fixture(autouse=True)
def fake_question_embedding(monkeypatch):
    def fake_create_embedding(text):
        return np.array(FAKE_VECTORS[text])

    monkeypatch.setattr(vector_store, "create_embedding", fake_create_embedding)


def test_empty_chunks_raise_error():
    with pytest.raises(ValueError):
        create_vector_store([])


def test_search_returns_the_right_chunk_with_document_id():
    chunks = make_chunks()
    index = create_vector_store(chunks)

    results = search_vector_store("dogs", index, chunks, top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == "text about dogs"
    assert results[0]["document_id"] == "id-1"
    assert results[0]["page"] == 2


def test_top_k_bigger_than_index_is_limited():
    chunks = make_chunks()
    index = create_vector_store(chunks)

    # min_score=-1 so no result is filtered out by the score
    results = search_vector_store("cats", index, chunks, top_k=50, min_score=-1)

    assert len(results) == 3


def test_invalid_top_k_raises_error():
    chunks = make_chunks()
    index = create_vector_store(chunks)

    with pytest.raises(ValueError):
        search_vector_store("cats", index, chunks, top_k=0)


# tmp_path is a temporary folder that pytest creates and deletes for us
def test_save_and_load_keep_the_link_between_vector_and_chunk(tmp_path):
    chunks = make_chunks()
    index = create_vector_store(chunks)
    save_vector_store(index, chunks, str(tmp_path))

    loaded_index, loaded_chunks = load_vector_store(str(tmp_path))

    assert loaded_index.ntotal == 3
    results = search_vector_store("cars", loaded_index, loaded_chunks, top_k=1)
    assert results[0]["document_id"] == "id-2"


def test_load_rejects_old_index_without_document_id(tmp_path):
    chunks = make_chunks()
    index = create_vector_store(chunks)
    save_vector_store(index, chunks, str(tmp_path))

    # simulate an old index: remove document_id from the saved file
    chunks_path = os.path.join(tmp_path, CHUNKS_FILE)
    with open(chunks_path, encoding="utf-8") as f:
        saved = json.load(f)
    for chunk in saved:
        del chunk["document_id"]
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(saved, f)

    with pytest.raises(ValueError):
        load_vector_store(str(tmp_path))


def test_load_rejects_wrong_number_of_chunks(tmp_path):
    chunks = make_chunks()
    index = create_vector_store(chunks)
    save_vector_store(index, chunks, str(tmp_path))

    # simulate a broken save: keep only 2 of the 3 chunks
    chunks_path = os.path.join(tmp_path, CHUNKS_FILE)
    with open(chunks_path, encoding="utf-8") as f:
        saved = json.load(f)
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(saved[:2], f)

    with pytest.raises(ValueError):
        load_vector_store(str(tmp_path))