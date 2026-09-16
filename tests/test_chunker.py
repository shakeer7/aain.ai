import pytest
from ingestion.chunker import SemanticChunker, Document

def test_chunk_quran_verse():
    chunker = SemanticChunker()
    verses = [
        {
            "surah": 1,
            "ayah": 1,
            "surah_name_ar": "الفاتحة",
            "surah_name_en": "Al-Fatihah",
            "text_ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            "text_en": "In the name of God, The Most Gracious, The Most Merciful",
            "juz": 1,
            "source": "Quran 1:1"
        }
    ]
    
    docs = chunker.chunk_quran(verses)
    assert len(docs) == 1
    doc = docs[0]
    assert isinstance(doc, Document)
    assert doc.id == "quran_1_1"
    assert doc.source == "Quran 1:1"
    assert doc.metadata["type"] == "quran"
    assert doc.metadata["surah"] == 1
    assert doc.metadata["ayah"] == 1

def test_chunk_hadiths():
    chunker = SemanticChunker()
    hadiths = [
        {
            "collection": "Sahih al-Bukhari",
            "book": "1",
            "hadith_number": "1",
            "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
            "text_en": "Actions are but by intentions.",
            "source": "Sahih al-Bukhari - Book 1, Hadith 1"
        }
    ]
    
    docs = chunker.chunk_hadiths(hadiths)
    assert len(docs) == 1
    doc = docs[0]
    assert isinstance(doc, Document)
    assert "hadith_sahih_al-bukhari_1_1" in doc.id
    assert doc.metadata["type"] == "hadith"
    assert doc.metadata["collection"] == "Sahih al-Bukhari"
