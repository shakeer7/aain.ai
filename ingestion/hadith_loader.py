import logging
from pathlib import Path
from typing import List, Dict, Any
from datasets import load_dataset
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HadithLoader:
    def __init__(self, processed_dir: Path):
        self.processed_dir = processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def load_hadiths(self) -> List[Dict[str, Any]]:
        """
        Loads Hadith collections. For this implementation, we use a public dataset from HuggingFace.
        e.g., 'bardsai/hadith' which contains Sahih Bukhari, Muslim, etc.
        """
        logger.info("Loading Hadith dataset from HuggingFace (bardsai/hadith)...")
        # Ensure you have accepted the dataset terms if required, or use a truly public one.
        # "bardsai/hadith" is a good proxy. We will load just a subset for the demo to save memory.
        try:
            dataset = load_dataset("bardsai/hadith", split="train")
            df = dataset.to_pandas()
            
            hadiths = []
            for _, row in df.iterrows():
                # Handling mapping based on typical hadith dataset schema
                collection = row.get("collection", "Unknown")
                book = row.get("book", "Unknown")
                hadith_no = row.get("hadith_no", "Unknown")
                
                hadiths.append({
                    "collection": collection,
                    "book": book,
                    "hadith_number": hadith_no,
                    "text_ar": row.get("text_ar", ""),
                    "text_en": row.get("text_en", ""),
                    "source": f"{collection} - Book {book}, Hadith {hadith_no}"
                })
                
            logger.info(f"Successfully loaded {len(hadiths)} hadiths.")
            return hadiths
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace dataset: {e}")
            logger.info("Falling back to a small sample dataset.")
            return self._get_mock_data()
            
    def _get_mock_data(self):
        return [
            {
                "collection": "Sahih al-Bukhari",
                "book": "1",
                "hadith_number": "1",
                "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
                "text_en": "Deeds are judged by motives (niyyah).",
                "source": "Sahih al-Bukhari - Book 1, Hadith 1"
            }
        ]

if __name__ == "__main__":
    loader = HadithLoader(Path("../data/processed"))
    hadiths = loader.load_hadiths()
    print(f"Sample hadith: {hadiths[0]}")
