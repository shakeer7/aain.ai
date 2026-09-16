from typing import List, Dict, Any
import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the cross-encoder for reranking. 
        Note: A multilingual cross-encoder would be ideal here if available.
        """
        logger.info(f"Loading cross-encoder model {model_name}...")
        self.model = CrossEncoder(model_name)
        logger.info("Reranker loaded successfully.")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Reranks the retrieved documents based on the query."""
        if not documents:
            return []
            
        # Pair query with each document text for cross-encoder
        # We use text_en as the cross-encoder is typically trained on English
        pairs = [[query, doc["text_en"]] for doc in documents]
        
        scores = self.model.predict(pairs)
        
        # Attach scores to documents
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])
            
        # Sort descending by rerank_score
        reranked_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        
        return reranked_docs[:top_k]
