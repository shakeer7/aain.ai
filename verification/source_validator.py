import re
from typing import List, Dict, Any

class SourceValidator:
    """
    A deterministic validation layer to ensure the generated text includes 
    the expected citation formats (e.g., [Quran X:Y] or [Hadith Collection - Book X, Hadith Y]).
    """
    def __init__(self):
        # basic pattern for brackets
        self.citation_pattern = re.compile(r"\[(.*?)\]")

    def validate_citations_present(self, answer: str, retrieved_docs: List[Dict[str, Any]]) -> bool:
        """
        Checks if the answer contains citations that match the provided documents.
        This is a fast heuristic check before falling back to the LLM-as-a-judge.
        """
        citations_in_text = self.citation_pattern.findall(answer)
        if not citations_in_text:
            # If no citations were generated but docs were provided, this is a flag.
            return False
            
        valid_sources = {doc["source"] for doc in retrieved_docs}
        
        # Check if at least one citation matches a valid source
        for citation in citations_in_text:
            # Simple substring match (e.g., "Source: Quran 2:255" -> "Quran 2:255")
            citation_clean = citation.replace("Source:", "").strip()
            if any(citation_clean in valid_src or valid_src in citation_clean for valid_src in valid_sources):
                return True
                
        return False
