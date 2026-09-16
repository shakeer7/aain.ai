from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import logging
from typing import List, Dict, Any

from ingestion.embedder import Embedder
from retrieval.vector_store import VectorStore
from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from llm.generator import Generator
from verification.citation_checker import CitationChecker
from verification.source_validator import SourceValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quran & Hadith RAG Assistant", version="1.0.0")

# Global instances for dependency injection
embedder = None
vector_store = None
retriever = None
reranker = None
generator = None
citation_checker = None
source_validator = None

@app.on_event("startup")
async def startup_event():
    global embedder, vector_store, retriever, reranker, generator, citation_checker, source_validator
    logger.info("Initializing ML components...")
    
    # Initialize components
    embedder = Embedder()
    vector_store = VectorStore()
    retriever = Retriever(vector_store, embedder)
    
    # Optional components based on resource availability
    try:
        reranker = Reranker()
    except Exception as e:
        logger.warning(f"Could not load reranker, falling back to dense retrieval only: {e}")
        reranker = None
        
    generator = Generator()
    citation_checker = CitationChecker()
    source_validator = SourceValidator()
    
    logger.info("Application startup complete.")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    verify_citations: bool = True

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    is_faithful: bool
    verification_reasoning: str

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        # 1. Retrieve
        retrieved_docs = retriever.retrieve(request.query, top_k=request.top_k * 2)
        
        # 2. Rerank
        if reranker and retrieved_docs:
            top_docs = reranker.rerank(request.query, retrieved_docs, top_k=request.top_k)
        else:
            top_docs = retrieved_docs[:request.top_k]
            
        if not top_docs:
            return QueryResponse(
                answer="I could not find any relevant sources.",
                sources=[],
                is_faithful=True,
                verification_reasoning="No sources found."
            )
            
        # 3. Generate
        answer = generator.generate_answer(request.query, top_docs)
        
        # 4. Verify (Deterministic)
        has_citations = source_validator.validate_citations_present(answer, top_docs)
        if not has_citations:
            logger.warning("No explicit valid citations found in answer.")
            
        # 5. Verify (LLM-as-a-judge)
        is_faithful = True
        reasoning = "Verification skipped."
        if request.verify_citations:
            is_faithful, reasoning = citation_checker.verify_answer(answer, top_docs)
            if not is_faithful:
                logger.warning(f"Hallucination detected: {reasoning}")
                # We could rewrite the answer here, but for now we just flag it.
                
        return QueryResponse(
            answer=answer,
            sources=top_docs,
            is_faithful=is_faithful,
            verification_reasoning=reasoning
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
