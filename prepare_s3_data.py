import os
import sys
import json
import logging
import subprocess
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EVAL_DIR = DATA_DIR / "eval"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

def get_s3_bucket_name() -> str:
    """Finds the S3 bucket created by Terraform."""
    try:
        cmd = ["aws", "s3", "ls"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 3 and parts[2].startswith("quran-hadith-rag-data-"):
                bucket = parts[2]
                logger.info(f"Detected target S3 bucket: {bucket}")
                return bucket
    except Exception as e:
        logger.warning(f"Could not auto-detect bucket: {e}")
    return "quran-hadith-rag-data-20260916053018162600000003"

def fetch_and_save_quran_edition(edition: str) -> dict:
    """Fetches a specific Quran edition from the Al Quran Cloud API and caches it locally."""
    file_path = RAW_DIR / f"quran_{edition}.json"
    if file_path.exists():
        logger.info(f"Using cached file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    logger.info(f"Downloading Quran edition '{edition}' from Al Quran Cloud API...")
    url = f"http://api.alquran.cloud/v1/quran/{edition}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()["data"]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved: {file_path}")
    return data

def prepare_merged_quran_data(arabic_data: dict, english_data: dict) -> list:
    """Merges Arabic and English Quran texts by Ayah with rich metadata."""
    logger.info("Merging Arabic and English Quran texts...")
    merged_verses = []

    for ar_surah, en_surah in zip(arabic_data["surahs"], english_data["surahs"]):
        surah_number = ar_surah["number"]
        surah_name_ar = ar_surah["name"]
        surah_name_en = ar_surah["englishName"]
        revelation_type = ar_surah.get("revelationType", "Meccan")

        for ar_ayah, en_ayah in zip(ar_surah["ayahs"], en_surah["ayahs"]):
            ayah_number = ar_ayah["numberInSurah"]
            merged_verses.append({
                "surah": surah_number,
                "surah_name_ar": surah_name_ar,
                "surah_name_en": surah_name_en,
                "revelation_type": revelation_type,
                "ayah": ayah_number,
                "juz": ar_ayah.get("juz", 1),
                "page": ar_ayah.get("page", 1),
                "text_ar": ar_ayah["text"],
                "text_en": en_ayah["text"],
                "source": f"Quran {surah_number}:{ayah_number}"
            })

    output_path = PROCESSED_DIR / "quran_merged.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_verses, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(merged_verses)} merged Quran verses to {output_path}")
    return merged_verses

def prepare_hadith_dataset() -> list:
    """Prepares authentic Hadiths with Arabic, English, and book/number metadata."""
    logger.info("Preparing foundational Hadith collection...")
    hadiths = [
        {
            "collection": "Sahih al-Bukhari",
            "book": "1",
            "hadith_number": "1",
            "chapter_ar": "كتاب بدء الوحي",
            "chapter_en": "Revelation",
            "text_ar": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى، فَمَنْ كَانَتْ هِجْرَتُهُ إِلَى دُنْيَا يُصِيبُهَا أَوْ إِلَى امْرَأَةٍ يَنْكِحُهَا فَهِجْرَتُهُ إِلَى مَا هَاجَرَ إِلَيْهِ.",
            "text_en": "Actions are judged by motives (intentions), so each man will have what he intended. Thus, he whose migration was to achieve some worldly benefit or to marry a woman, his migration was for that which he migrated.",
            "source": "Sahih al-Bukhari - Book 1, Hadith 1"
        },
        {
            "collection": "Sahih al-Bukhari",
            "book": "2",
            "hadith_number": "8",
            "chapter_ar": "كتاب الإيمان",
            "chapter_en": "Belief",
            "text_ar": "بُنِيَ الإِسْلاَمُ عَلَى خَمْسٍ: شَهَادَةِ أَنْ لاَ إِلَهَ إِلاَّ اللَّهُ وَأَنَّ مُحَمَّدًا رَسُولُ اللَّهِ، وَإِقَامِ الصَّلاَةِ، وَإِيتَاءِ الزَّكَاةِ، وَالحَجِّ، وَصَوْمِ رَمَضَانَ.",
            "text_en": "Islam is based on five principles: To testify that none has the right to be worshipped but Allah and Muhammad is Allah's Apostle; to offer the prayers dutifully; to pay Zakat; to perform Hajj; and to observe fast during Ramadan.",
            "source": "Sahih al-Bukhari - Book 2, Hadith 8"
        },
        {
            "collection": "Sahih al-Bukhari",
            "book": "2",
            "hadith_number": "13",
            "chapter_ar": "كتاب الإيمان",
            "chapter_en": "Belief",
            "text_ar": "لاَ يُؤْمِنُ أَحَدُكُمْ حَتَّى يُحِبَّ لأَخِيهِ مَا يُحِبُّ لِنَفْسِهِ.",
            "text_en": "None of you will have faith till he wishes for his (Muslim) brother what he likes for himself.",
            "source": "Sahih al-Bukhari - Book 2, Hadith 13"
        },
        {
            "collection": "Sahih Muslim",
            "book": "1",
            "hadith_number": "1",
            "chapter_ar": "كتاب الإيمان",
            "chapter_en": "The Book of Faith (Hadith Jibril)",
            "text_ar": "أَنْ تُؤْمِنَ بِاللَّهِ وَمَلاَئِكَتِهِ وَكُتُبِهِ وَرُسُلِهِ وَالْيَوْمِ الآخِرِ وَتُؤْمِنَ بِالْقَدَرِ خَيْرِهِ وَشَرِّهِ.",
            "text_en": "Faith is to believe in Allah, His Angels, His Books, His Messengers, the Last Day, and to believe in Divine Destiny, both the good and evil thereof.",
            "source": "Sahih Muslim - Book 1, Hadith 1"
        },
        {
            "collection": "Sahih Muslim",
            "book": "45",
            "hadith_number": "6518",
            "chapter_ar": "كتاب البر والصلة والآداب",
            "chapter_en": "Virtue, Good Manners and Joining Ties",
            "text_ar": "مَثَلُ الْمُؤْمِنِينَ فِي تَوَادِّهِمْ وَتَرَاحُمِهِمْ وَتَعَاطُفِهِمْ مَثَلُ الْجَسَدِ إِذَا اشْتَكَى مِنْهُ عُضْوٌ تَدَاعَى لَهُ سَائِرُ الْجَسَدِ بِالسَّهَرِ وَالْحُمَّى.",
            "text_en": "The similitude of believers in regard to mutual love, affection, and fellow-feeling is that of one body; when any limb aches, the whole body aches, because of sleeplessness and fever.",
            "source": "Sahih Muslim - Book 45, Hadith 6518"
        },
        {
            "collection": "Sahih al-Bukhari",
            "book": "78",
            "hadith_number": "5971",
            "chapter_ar": "كتاب الأدب",
            "chapter_en": "Good Manners",
            "text_ar": "جَاءَ رَجُلٌ إِلَى رَسُولِ اللَّهِ صلى الله عليه وسلم فَقَالَ: يَا رَسُولَ اللَّهِ، مَنْ أَحَقُّ النَّاسِ بِحُسْنِ صَحَابَتِي؟ قَالَ: أُمُّكَ. قَالَ: ثُمَّ مَنْ؟ قَالَ: ثُمَّ أُمُّكَ. قَالَ: ثُمَّ مَنْ؟ قَالَ: ثُمَّ أُمُّكَ. قَالَ: ثُمَّ مَنْ؟ قَالَ: ثُمَّ أَبُوكَ.",
            "text_en": "A man came to Allah's Messenger and said, 'O Allah's Messenger! Who is more entitled to be treated with the best companionship by me?' The Prophet said, 'Your mother.' The man said, 'Who is next?' The Prophet said, 'Your mother.' The man further said, 'Who is next?' The Prophet said, 'Your mother.' The man asked for the fourth time, 'Who is next?' The Prophet said, 'Your father.'",
            "source": "Sahih al-Bukhari - Book 78, Hadith 5971"
        }
    ]

    output_path = PROCESSED_DIR / "hadith_unified.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hadiths, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(hadiths)} foundational Hadiths to {output_path}")
    return hadiths

def prepare_golden_eval_dataset():
    """Creates a golden evaluation dataset for RAGAS benchmarks."""
    eval_data = {
        "benchmark_suite": "Islamic RAG Grounded Evaluation",
        "version": "1.0",
        "queries": [
            {
                "question": "What are the five pillars of Islam according to Hadith?",
                "ground_truth": "The five pillars of Islam are: testifying that none has the right to be worshipped but Allah and Muhammad is His Messenger, establishing the prayers, giving Zakat, performing Hajj, and fasting during Ramadan.",
                "expected_sources": ["Sahih al-Bukhari - Book 2, Hadith 8"]
            },
            {
                "question": "What does Islam teach about intentions and motives?",
                "ground_truth": "Actions are judged and rewarded strictly according to intentions and motives.",
                "expected_sources": ["Sahih al-Bukhari - Book 1, Hadith 1"]
            },
            {
                "question": "What does the Quran say about God being with the patient?",
                "ground_truth": "The Quran commands the believers to seek help through patience and prayer, and affirms that God is indeed with those who are patient.",
                "expected_sources": ["Quran 2:153"]
            },
            {
                "question": "Who is most entitled to good companionship and dutiful treatment according to the Prophet?",
                "ground_truth": "The mother is entitled to the highest companionship and honor, repeated three times by the Prophet, followed by the father.",
                "expected_sources": ["Sahih al-Bukhari - Book 78, Hadith 5971"]
            },
            {
                "question": "What is the virtue and meaning of Ayat al-Kursi?",
                "ground_truth": "Ayat al-Kursi (Quran 2:255) affirms that Allah is the Ever-Living, Sustainer of all existence; neither slumber nor sleep overtakes Him; to Him belongs all that is in the heavens and the earth.",
                "expected_sources": ["Quran 2:255"]
            }
        ]
    }

    eval_file = EVAL_DIR / "golden_qa_testset.json"
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved evaluation testset to {eval_file}")

def upload_all_data_to_s3(bucket_name: str):
    """Uploads raw, processed, and evaluation data directly to the S3 bucket using AWS CLI."""
    logger.info(f"Starting multi-tier upload to s3://{bucket_name}/ ...")

    # 1. Sync raw directory
    logger.info("Uploading raw datasets...")
    subprocess.run(["aws", "s3", "sync", str(RAW_DIR), f"s3://{bucket_name}/raw/"], check=True)

    # 2. Sync processed directory
    logger.info("Uploading processed & unified datasets...")
    subprocess.run(["aws", "s3", "sync", str(PROCESSED_DIR), f"s3://{bucket_name}/processed/"], check=True)

    # 3. Sync evaluation directory
    logger.info("Uploading evaluation benchmarks...")
    subprocess.run(["aws", "s3", "sync", str(EVAL_DIR), f"s3://{bucket_name}/eval/"], check=True)

    logger.info("Verifying S3 bucket contents...")
    result = subprocess.run(["aws", "s3", "ls", f"s3://{bucket_name}/", "--recursive"], capture_output=True, text=True, check=True)
    print("\n" + "="*60)
    print(f"S3 DATA LAKE CONTENTS (s3://{bucket_name}/)")
    print("="*60)
    print(result.stdout)
    print("="*60)

def main():
    bucket_name = get_s3_bucket_name()
    
    # 1. Fetch Arabic Quran
    arabic_data = fetch_and_save_quran_edition("quran-uthmani")

    # 2. Fetch English Quran (Muhammad Asad)
    english_data = fetch_and_save_quran_edition("en.asad")

    # 3. Merge Quran into Ayah-by-Ayah records
    prepare_merged_quran_data(arabic_data, english_data)

    # 4. Prepare authentic Hadith collection
    prepare_hadith_dataset()

    # 5. Prepare golden evaluation QA dataset
    prepare_golden_eval_dataset()

    # 6. Upload everything to Amazon S3
    upload_all_data_to_s3(bucket_name)

if __name__ == "__main__":
    main()
