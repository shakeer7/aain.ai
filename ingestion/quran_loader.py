import requests
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuranLoader:
    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.arabic_edition = "quran-uthmani"
        self.english_edition = "en.asad" # Muhammad Asad translation
        
    def fetch_quran(self, edition: str) -> Dict[str, Any]:
        """Fetch the entire Quran for a specific edition from Al Quran Cloud API."""
        file_path = self.raw_dir / f"quran_{edition}.json"
        
        if file_path.exists():
            logger.info(f"Loading {edition} from local cache...")
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
                
        logger.info(f"Fetching {edition} from API...")
        url = f"http://api.alquran.cloud/v1/quran/{edition}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["data"]
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return data

    def load_and_merge(self) -> List[Dict[str, Any]]:
        """Loads both Arabic and English texts and merges them by Ayah."""
        arabic_data = self.fetch_quran(self.arabic_edition)
        english_data = self.fetch_quran(self.english_edition)
        
        merged_verses = []
        
        # Both APIs return a list of surahs, each with ayahs
        for ar_surah, en_surah in zip(arabic_data["surahs"], english_data["surahs"]):
            surah_number = ar_surah["number"]
            surah_name_ar = ar_surah["name"]
            surah_name_en = ar_surah["englishName"]
            
            for ar_ayah, en_ayah in zip(ar_surah["ayahs"], en_surah["ayahs"]):
                ayah_number = ar_ayah["numberInSurah"]
                
                merged_verses.append({
                    "surah": surah_number,
                    "surah_name_ar": surah_name_ar,
                    "surah_name_en": surah_name_en,
                    "ayah": ayah_number,
                    "text_ar": ar_ayah["text"],
                    "text_en": en_ayah["text"],
                    "juz": ar_ayah["juz"],
                    "source": f"Quran {surah_number}:{ayah_number}"
                })
                
        logger.info(f"Successfully loaded {len(merged_verses)} verses.")
        return merged_verses

if __name__ == "__main__":
    loader = QuranLoader(Path("../data/raw"))
    verses = loader.load_and_merge()
    print(f"Sample verse: {verses[0]}")
