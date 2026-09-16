import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in python path
root_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(root_dir))

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from ingestion.quran_loader import QuranLoader
from ingestion.hadith_loader import HadithLoader
from ingestion.chunker import SemanticChunker
from ingestion.embedder import Embedder
from retrieval.vector_store import VectorStore

def run_ingestion():
    raw_dir = root_dir / "data" / "raw"
    processed_dir = root_dir / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Quran Data
    logger.info("=== Step 1: Loading Quran Data ===")
    quran_loader = QuranLoader(raw_dir=raw_dir)
    quran_verses = quran_loader.load_and_merge()
    logger.info(f"Loaded {len(quran_verses)} Quran verses.")
    
    # 2. Load Hadith Data
    logger.info("=== Step 2: Loading Hadith Data ===")
    hadith_loader = HadithLoader(processed_dir=processed_dir)
    hadiths = hadith_loader.load_hadiths()
    logger.info(f"Loaded {len(hadiths)} Hadiths.")
    
    # 3. Semantic Chunking
    logger.info("=== Step 3: Chunking Documents ===")
    chunker = SemanticChunker()
    quran_docs = chunker.chunk_quran(quran_verses)
    hadith_docs = chunker.chunk_hadiths(hadiths)
    all_docs = quran_docs + hadith_docs
    logger.info(f"Total documents prepared: {len(all_docs)} (Quran: {len(quran_docs)}, Hadith: {len(hadith_docs)})")
    
    # 4. Multilingual Embeddings
    logger.info("=== Step 4: Generating Dense Embeddings ===")
    embedder = Embedder()
    texts_to_embed = [doc.text_en for doc in all_docs]
    embeddings = embedder.embed_texts(texts_to_embed)
    
    # 5. Populate Qdrant Vector Store
    logger.info("=== Step 5: Upserting to Qdrant ===")
    vector_store = VectorStore(vector_size=embedder.embedding_dimension)
    vector_store.add_documents(documents=all_docs, embeddings=embeddings)
    
    logger.info("=== Ingestion Finished Successfully! ===")

if __name__ == "__main__":
    run_ingestion()
