from typing import List, Dict, Any
from retrieval.vector_store import VectorStore
from ingestion.embedder import Embedder

class Retriever:
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant documents for a given query."""
        query_embedding = self.embedder.embed_query(query)
        
        results = self.vector_store.client.search(
            collection_name=self.vector_store.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        retrieved_docs = []
        for res in results:
            retrieved_docs.append({
                "score": res.score,
                "doc_id": res.payload["doc_id"],
                "text_en": res.payload["text_en"],
                "text_ar": res.payload["text_ar"],
                "source": res.payload["source"],
                "metadata": res.payload["metadata"]
            })
            
        return retrieved_docs
