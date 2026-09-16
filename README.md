# Quran & Hadith RAG Assistant

A robust, end-to-end Retrieval-Augmented Generation (RAG) assistant for Islamic texts (Quran and Hadith). 
This project leverages modern MLOps practices, including semantic search, hybrid retrieval, citation verification, and deployment on Kubernetes.

## Features
- **Data Ingestion**: Automated loading and chunking of Quranic verses and Hadiths.
- **Hybrid Search**: Dense embeddings and BM25 sparse retrieval using Qdrant.
- **Reranking**: Improved retrieval accuracy with cross-encoder reranking.
- **Verifiable Generation**: Strict prompting and citation checking to prevent hallucinations on sacred texts.
- **Evaluation**: RAGAS-based evaluation metrics for retrieval and faithfulness.
- **MLOps**: Dockerized application with Terraform infrastructure scripts for AWS EKS deployment.

## Project Structure
- `ingestion/`: Data loaders, chunkers, and embedders.
- `retrieval/`: Vector store management, hybrid retrieval, and reranking.
- `llm/`: Prompts and LLM generation logic.
- `verification/`: Citation checking and hallucination prevention.
- `api/`: FastAPI endpoints.
- `evaluation/`: RAGAS evaluation suite.
- `infrastructure/`: Terraform scripts for EKS.
- `k8s/`: Kubernetes deployment manifests.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
