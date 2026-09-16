# 📖 aain.ai is a Quran & Hadith RAG Assistant

> A production-grade Retrieval-Augmented Generation (RAG) assistant for Islamic texts (Quran and Hadith), built with hybrid search, reranking, and strict citation verification to prevent hallucinations on sacred texts.

<!-- 
  PLACEHOLDER: Add a banner/hero screenshot of your app here.
  Example: ![App Banner](./assets/banner.png)
-->
![Banner Placeholder](https://via.placeholder.com/1200x400?text=Add+Your+Project+Banner+Here)

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue.svg">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Ready-2496ED.svg">
  <img alt="Kubernetes" src="https://img.shields.io/badge/Kubernetes-EKS-326CE5.svg">
  <img alt="Terraform" src="https://img.shields.io/badge/Terraform-IaC-7B42BC.svg">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg">
</p>

---

## ✨ Overview

This project is an end-to-end RAG pipeline purpose-built for religious texts, where accuracy and verifiability matter more than anywhere else. It combines dense embeddings with sparse BM25 retrieval, cross-encoder reranking, and a strict citation-checking layer so that every answer traces back to a real, verifiable source in the Quran or Hadith collections — never a hallucinated one.

The system is fully containerized and deployable on AWS EKS via Terraform and Kubernetes manifests, following modern MLOps practices from ingestion to evaluation.

---

## 🖼️ Screenshots / Demo

<!-- 
  PLACEHOLDER: Paste your screenshots or a demo GIF below.
  Example:
  ![Chat UI](./assets/chat-ui.png)
  ![Citation Verification](./assets/citation-check.png)
-->

| | |
|---|---|
| ![Screenshot 1 Placeholder](https://via.placeholder.com/500x300?text=Screenshot+1) | ![Screenshot 2 Placeholder](https://via.placeholder.com/500x300?text=Screenshot+2) |
| ![Screenshot 3 Placeholder](https://via.placeholder.com/500x300?text=Screenshot+3) | ![Screenshot 4 Placeholder](https://via.placeholder.com/500x300?text=Screenshot+4) |

---

## 🚀 Features

- **📥 Data Ingestion** — Automated loading and chunking of Quranic verses and Hadiths
- **🔍 Hybrid Search** — Dense embeddings + BM25 sparse retrieval powered by Qdrant
- **📊 Reranking** — Cross-encoder reranking for improved retrieval accuracy
- **✅ Verifiable Generation** — Strict prompting and citation checking to prevent hallucinations on sacred texts
- **📈 Evaluation** — RAGAS-based metrics for retrieval quality and faithfulness
- **⚙️ MLOps-Ready** — Dockerized application with Terraform infrastructure for AWS EKS deployment
- **☸️ Kubernetes Native** — Ships with production-ready K8s manifests

---

## 🏗️ Architecture

<!-- 
  PLACEHOLDER: Add an architecture diagram here.
  Example: ![Architecture Diagram](./assets/architecture.png)
-->
![Architecture Diagram Placeholder](https://via.placeholder.com/900x450?text=Add+Architecture+Diagram+Here)

```
User Query → API (FastAPI) → Hybrid Retrieval (Qdrant + BM25)
           → Reranker (Cross-Encoder) → LLM Generation
           → Citation Verification → Verified Response
```

---

## 📂 Project Structure

```
quran-hadith-rag/
├── api/                        # FastAPI endpoints
├── data/                       # Raw and processed source texts
├── ingestion/                  # Data loaders, chunkers, and embedders
├── retrieval/                  # Vector store management, hybrid retrieval, reranking
├── llm/                        # Prompts and LLM generation logic
├── verification/               # Citation checking and hallucination prevention
├── evaluation/                 # RAGAS evaluation suite
├── infrastructure/terraform/   # Terraform scripts for EKS
├── k8s/                        # Kubernetes deployment manifests
├── frontend/                   # Frontend application
├── tests/                      # Test suite
├── Dockerfile
├── ingest.py
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Vector Store | Qdrant (hybrid: dense + BM25) |
| Reranking | Cross-Encoder |
| API | FastAPI |
| Evaluation | RAGAS |
| Containerization | Docker |
| Infrastructure | Terraform (AWS EKS) |
| Orchestration | Kubernetes |

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized deployment)
- AWS account (optional, for EKS deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/shakeer7/quran-hadith-rag.git
cd quran-hadith-rag

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Ingest the data

```bash
python ingest.py
```

### Run the API

```bash
uvicorn api.main:app --reload
```

### Run with Docker

```bash
docker build -t quran-hadith-rag .
docker run -p 8000:8000 quran-hadith-rag
```

### Deploy to AWS EKS

```bash
cd infrastructure/terraform
terraform init
terraform apply

kubectl apply -f k8s/
```

---

## 🧪 Evaluation

This project uses **RAGAS** to measure retrieval and generation quality:

```bash
pytest evaluation/
```

<!-- PLACEHOLDER: Add a screenshot of your evaluation results/dashboard here -->
![Evaluation Results Placeholder](https://via.placeholder.com/900x300?text=Add+Evaluation+Results+Here)

---

## 🙏 A Note on Accuracy

Working with the Quran and Hadith demands a higher bar than typical RAG applications. This system is designed to:
- Never generate content not grounded in retrieved source text
- Flag low-confidence or unverifiable citations
- Prefer refusing to answer over guessing

That said, this tool is an aid for research and study — always verify important religious rulings with a qualified scholar.

---

## 🗺️ Roadmap

- [ ] Multi-language support (Arabic, Urdu, English)
- [ ] Tafsir (exegesis) integration
- [ ] Chain-of-custody citation scoring
- [ ] Public web demo

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/shakeer7/quran-hadith-rag/issues).

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Shakeer**
GitHub: [@shakeer7](https://github.com/shakeer7)
