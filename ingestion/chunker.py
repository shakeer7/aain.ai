from typing import List, Dict, Any
from pydantic import BaseModel, Field

class Document(BaseModel):
    id: str
    text_en: str
    text_ar: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SemanticChunker:
    """
    Chunks Quran and Hadith data semantically.
    For Quran: 1 Ayah = 1 Chunk (mostly fits within embedding token limits).
    For Hadith: 1 Hadith = 1 Chunk.
    """
    
    def chunk_quran(self, verses: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        for v in verses:
            doc_id = f"quran_{v['surah']}_{v['ayah']}"
            doc = Document(
                id=doc_id,
                text_en=v["text_en"],
                text_ar=v["text_ar"],
                source=v["source"],
                metadata={
                    "type": "quran",
                    "surah": v["surah"],
                    "ayah": v["ayah"],
                    "surah_name_en": v["surah_name_en"]
                }
            )
            documents.append(doc)
        return documents

    def chunk_hadiths(self, hadiths: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        for idx, h in enumerate(hadiths):
            collection_safe = h["collection"].replace(" ", "_").lower()
            doc_id = f"hadith_{collection_safe}_{h['book']}_{h['hadith_number']}_{idx}"
            doc = Document(
                id=doc_id,
                text_en=h["text_en"],
                text_ar=h["text_ar"],
                source=h["source"],
                metadata={
                    "type": "hadith",
                    "collection": h["collection"],
                    "book": h["book"],
                    "hadith_number": h["hadith_number"]
                }
            )
            documents.append(doc)
        return documents
