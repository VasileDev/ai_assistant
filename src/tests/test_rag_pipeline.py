import pytest
from openai import APIConnectionError

from rag import generator, rag_pipeline
from rag.rag_pipeline import NO_ANSWER_MESSAGE, LLMError, answer_question

# one chunk, as if the search had found it
FOUND_CHUNK = {
    "text": "The Duster has 4x4.",
    "page": 3,
    "document_name": "Dacia Duster.pdf",
    "document_id": "abc",
    "score": 0.81234,
}


# the search finds the chunk and the LLM answers -> answer + structured sources
def test_answer_comes_with_structured_sources(monkeypatch):
    def fake_retrieve(**kwargs):
        return [FOUND_CHUNK]

    def fake_llm(**kwargs):
        return "Yes, it has 4x4."

    monkeypatch.setattr(rag_pipeline, "retrieve_context", fake_retrieve)
    monkeypatch.setattr(rag_pipeline, "generate_answer", fake_llm)

    result = answer_question("Does it have 4x4?", index=None, embedded_chunks=[])

    assert result["answer"] == "Yes, it has 4x4."
    assert len(result["sources"]) == 1
    assert result["sources"][0]["document_name"] == "Dacia Duster.pdf"
    assert result["sources"][0]["document_id"] == "abc"
    assert result["sources"][0]["page"] == 3
    assert result["sources"][0]["score"] == 0.812  # rounded to 3 decimals


# the search finds nothing -> the LLM must NOT be called (it costs money)
def test_nothing_found_does_not_call_the_llm(monkeypatch):
    def fake_retrieve(**kwargs):
        return []

    def llm_must_not_be_called(**kwargs):
        raise AssertionError("the LLM was called")

    monkeypatch.setattr(rag_pipeline, "retrieve_context", fake_retrieve)
    monkeypatch.setattr(rag_pipeline, "generate_answer", llm_must_not_be_called)

    result = answer_question("Unrelated?", index=None, embedded_chunks=[])

    assert result == {"answer": NO_ANSWER_MESSAGE, "sources": []}


# the LLM says it can't find the answer -> no sources shown
def test_llm_says_not_found_gives_no_sources(monkeypatch):
    def fake_retrieve(**kwargs):
        return [FOUND_CHUNK]

    def fake_llm(**kwargs):
        return NO_ANSWER_MESSAGE

    monkeypatch.setattr(rag_pipeline, "retrieve_context", fake_retrieve)
    monkeypatch.setattr(rag_pipeline, "generate_answer", fake_llm)

    result = answer_question("Price?", index=None, embedded_chunks=[])

    assert result == {"answer": NO_ANSWER_MESSAGE, "sources": []}


# no API key -> our LLMError, not a crash
def test_missing_api_key_raises_llm_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)  # remove the key only for this test
    monkeypatch.setattr(generator, "client", None)  # forget any client created before

    with pytest.raises(LLMError):
        generator.call_llm("hello")


# OpenAI is down -> our LLMError
def test_openai_failure_raises_llm_error(monkeypatch):
    # a fake client that always fails like a lost internet connection
    class BrokenResponses:
        def create(self, **kwargs):
            raise APIConnectionError(request=None)

    class BrokenClient:
        responses = BrokenResponses()

    monkeypatch.setattr(generator, "client", BrokenClient())

    with pytest.raises(LLMError):
        generator.call_llm("hello")


def test_context_contains_document_and_page():
    context = generator.build_context([FOUND_CHUNK])
    assert "[Dacia Duster.pdf | Page: 3]" in context