# AI Assistant

Upload one or more text-based PDF documents, then ask questions grounded in their contents. Answers include the source document and page.

## Requirements

- Python 3.11 or newer
- An OpenAI API key

## Run locally

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with `.venv\\Scripts\\Activate.ps1` instead.

Activate the environment, then install the dependencies and configure the API key:

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`, then start the server:

```bash
cd src
python -m uvicorn main:app --reload
```

Open <http://127.0.0.1:8000/app> for the web interface or <http://127.0.0.1:8000/docs> for the API. The embedding model downloads the first time documents are uploaded.

## Use

Choose up to 10 PDFs (maximum 20 MiB each) and upload them. A successful upload replaces the active document set. If validation or indexing fails, the previous index stays available. Scanned PDFs need OCR and are not supported by this version.

The index and temporary uploads are stored under `data/` and are ignored by Git. This MVP keeps one active document set for the whole server; it does not provide separate users or document collections.

## Tests

From the repository root, run:

```bash
python -m pytest src/tests -q
```

Tests use small fake vectors where possible and do not call the OpenAI API.
