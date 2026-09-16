import pytest
from verification.source_validator import SourceValidator

def test_citation_validator_valid_citation():
    validator = SourceValidator()
    retrieved_docs = [
        {"source": "Quran 2:255"},
        {"source": "Sahih al-Bukhari - Book 1, Hadith 1"}
    ]
    
    answer_with_quran = "Allah! There is no deity except Him, the Ever-Living [Quran 2:255]."
    assert validator.validate_citations_present(answer_with_quran, retrieved_docs) is True
    
    answer_with_hadith = "Deeds are judged by intentions [Sahih al-Bukhari - Book 1, Hadith 1]."
    assert validator.validate_citations_present(answer_with_hadith, retrieved_docs) is True

def test_citation_validator_missing_citation():
    validator = SourceValidator()
    retrieved_docs = [
        {"source": "Quran 2:255"}
    ]
    
    # Text with no brackets
    answer_no_brackets = "Allah is the Ever-Living, the Sustainer of all existence."
    assert validator.validate_citations_present(answer_no_brackets, retrieved_docs) is False

def test_citation_validator_unmatched_citation():
    validator = SourceValidator()
    retrieved_docs = [
        {"source": "Quran 2:255"}
    ]
    
    # Citation not in retrieved sources
    answer_wrong_source = "Allah loves those who are patient [Quran 3:146]."
    assert validator.validate_citations_present(answer_wrong_source, retrieved_docs) is False
