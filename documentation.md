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