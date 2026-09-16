import os
import uuid
import logging
from typing import List, Dict, Any
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from ingestion.chunker import Document

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(
        self,
        collection_name: str = "quran_hadith",
        vector_size: int = 384,
        db_path: str = None
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        qdrant_host = os.getenv("QDRANT_HOST")
        if qdrant_host and qdrant_host.strip():
            qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
            logger.info(f"Connecting to remote Qdrant cluster at {qdrant_host}:{qdrant_port}...")
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        else:
            default_path = Path(__file__).parent.parent / "data" / "qdrant_db"
            resolved_path = Path(db_path) if db_path else default_path
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local persistent Qdrant at {resolved_path}...")
            self.client = QdrantClient(path=str(resolved_path))
            
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Creating collection '{self.collection_name}' in Qdrant...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
        else:
            logger.info(f"Collection '{self.collection_name}' already exists.")

    def add_documents(self, documents: List[Document], embeddings: List[List[float]], batch_size: int = 100):
        """Adds documents and their corresponding dense vectors to Qdrant."""
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match.")
            
        points = []
        for doc, emb in zip(documents, embeddings):
            # Deterministic UUID from document ID
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.id))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=emb,
                    payload={
                        "doc_id": doc.id,
                        "text_en": doc.text_en,
                        "text_ar": doc.text_ar,
                        "source": doc.source,
                        "metadata": doc.metadata
                    }
                )
            )
            
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[i:i+batch_size]
            )
        logger.info(f"Successfully added {len(points)} documents to Qdrant.")
