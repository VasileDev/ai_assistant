import pytest

from ingestion.text_splitter import chunking_pages


# removes all spaces, so we can compare only the letters
def without_spaces(text: str) -> str:
    return "".join(text.split())


# with overlap=0, all the chunks glued together must contain every letter of the page
def assert_no_text_lost(page: str, chunk_size: int):
    chunks = chunking_pages([page], chunk_size=chunk_size, overlap=0)

    rebuilt = ""
    for chunk in chunks:
        rebuilt = rebuilt + chunk["text"]

    assert without_spaces(rebuilt) == without_spaces(page)


# the old bug: "fghijk" disappeared
def test_long_word_is_not_lost():
    assert_no_text_lost("abcdefghijk next", chunk_size=5)


def test_long_url_is_not_lost():
    page = "see https://example.com/a/very/long/path/to/some/document.pdf for details"
    assert_no_text_lost(page, chunk_size=20)


def test_normal_text_is_not_lost():
    page = "the quick brown fox jumps over the lazy dog"
    assert_no_text_lost(page, chunk_size=15)


def test_empty_page_gives_no_chunks():
    assert chunking_pages(["", "   "]) == []


def test_page_numbers_start_at_one():
    chunks = chunking_pages(["first page", "second page"], chunk_size=100, overlap=0)
    assert chunks[0]["page"] == 1
    assert chunks[1]["page"] == 2


def test_invalid_parameters():
    # pytest.raises checks that the function really raises the error
    with pytest.raises(ValueError):
        chunking_pages(["text"], chunk_size=0)

    with pytest.raises(ValueError):
        chunking_pages(["text"], chunk_size=10, overlap=10)