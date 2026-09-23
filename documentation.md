Project Structure:
ai-knowledge-assistant/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── Dockerfile
│
├── data/
│   └── documents/
│
├── src/
│   ├── main.py
│   │
│   ├── ingestion/
│   │   ├── document_loader.py  #vas
│   │   ├── text_splitter.py    #vas
│   │   └── pipeline.py         #vas
│   │
│   ├── embeddings/
│   │   ├── embedding_model.py  #raul
│   │   └── vector_store.py     #raul
│   │
│   ├── rag/
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── rag_pipeline.py
│   │
│   ├── agents/
│   │   ├── agent.py
│   │   └── tools.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   └── evaluation/
│       ├── latency.py
│       └── evaluation.py
│
├── frontend/
│   └── app.py
│
├── tests/
│
├── docker/
│
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
│
└── helm/
    └── ai-assistant/


Stages of the learning process

Stage 0: Python Fundamentals
-variables
-lists
-dictionaries
-functions
-classes
-imports
-files
-exceptions
-virtual environments
-pip

Stage 1: Creating the repository
-bash commands
-virtual environment
-requirements.txt & .gitignore

Stage 2: Understanding what's a LLM
-prompt
-model
-input
-output
-tokens
-context window
-temperature
-latency

Vids I watched: 
https://www.youtube.com/watch?v=awGeJd16WZI
https://www.youtube.com/watch?v=QF0v3dXg0Kg

Stage 3: Embeddings

# Retrieval Pipeline Improvements - GPT-6

These tasks strengthen the existing PDF ingestion and search pipeline before adding answer generation and the web interface.

## Correctness

- [ ] Handle searches requesting more results than the index contains.
  - Limit `top_k` to the number of indexed chunks.
  - Ignore negative result IDs returned by FAISS.
  - Return an empty list when searching an empty index.
  - Reject non-positive `top_k` values.

- [ ] Handle documents with no readable text.
  - Check for empty chunks before creating embeddings or an index.
  - Return a clear message: "No readable text found in this document."
  - Treat OCR for scanned PDFs as a future enhancement.

- [ ] Validate chunking parameters.
  - Require `chunk_size > 0`.
  - Require `0 <= overlap < chunk_size`.
  - Negative overlap currently allows text to be skipped.

- [ ] Fix file paths in the demo scripts.
  - Use `pathlib` to resolve sample files relative to the project or script.
  - Ensure scripts work when launched from the repository root.

## Source Tracking and Retrieval Results

- [ ] Preserve source metadata throughout the pipeline.
  - Include `document_id`, `filename`, `chunk_id`, `page`, and `text`.
  - Preserve these fields when adding embeddings.
  - Ensure results can identify the correct document and page.

- [ ] Return similarity scores with search results.
  - Keep each score paired with its matching chunk.
  - Use scores to inspect retrieval quality; they are not confidence probabilities.

## Embedding Improvements

- [ ] Avoid loading the embedding model during module import.
  - Load it lazily through a cached function, or initialize it explicitly once.
  - Allow tests to use fake embeddings without downloading a model.

- [ ] Generate embeddings in batches.
  - Pass multiple chunk texts to `model.encode()`.
  - Preserve the correspondence between vectors and chunk metadata.

- [ ] Correct the return annotation of `create_embedding()`.
  - It returns a numerical array, not `list[dict]`.

## Persistence

- [ ] Save and reload the vector index and chunk metadata.
  - Save the FAISS index and a corresponding metadata file.
  - Preserve the exact ordering between index entries and chunks.
  - Record the embedding model and chunking settings.
  - Rebuild the index when incompatible settings change.
  - Validate that the index and metadata belong together when loading.

## Setup and Documentation

- [ ] Make the development environment reproducible.
  - Document a supported Python version.
  - Use a virtual environment.
  - Pin dependency versions after verifying compatibility.

- [ ] Expand the README.
  - Include installation and demo commands.
  - Explain the initial embedding-model download.
  - Distinguish implemented components from planned components.

## Tests

- [ ] Add automated tests for:
  - Empty documents and empty chunk lists.
  - Invalid chunk sizes and overlap values.
  - Expected overlap and preserved page numbering.
  - Searches requesting more results than available.
  - Empty-index searches and invalid `top_k`.
  - Source metadata preserved through embedding and retrieval.
  - Index save/load preserving chunk-to-vector correspondence.

- [ ] Use fake embeddings for most tests.
  - Keep a separate integration test for the real embedding model and FAISS.

## Future Quality Improvement

- [ ] Consider paragraph- or sentence-aware chunking.
  - The current character-based splitter can cut words and ideas.
  - Evaluate retrieval quality before replacing the current approach.

## Suggested Implementation Order

1. Search edge cases and empty-document handling.
2. Chunking validation and portable file paths.
3. Source metadata and similarity scores.
4. Automated tests for the corrected behavior.
5. Model loading and batch embeddings.
6. Index persistence.
7. Reproducible setup and documentation.

## Review Status

All nine Python files passed syntax parsing, and basic chunking checks passed.
The complete retrieval demo has not yet been run in the review environment
because the PDF, embedding, and FAISS dependencies were not installed.