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



python -m uvicorn main:app --reload