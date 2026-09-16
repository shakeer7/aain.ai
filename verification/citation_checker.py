import os
import logging
import json
from typing import List, Dict, Any, Tuple
from google import genai
from google.genai import types
from llm.prompts import CITATION_VERIFICATION_PROMPT

logger = logging.getLogger(__name__)

class CitationChecker:
    def __init__(self, model_name: str = None):
        self.client = genai.Client()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        context_parts = []
        for doc in documents:
            source = doc.get("source", "Unknown Source")
            text_en = doc.get("text_en", "")
            context_parts.append(f"[Source: {source}]\n{text_en}\n")
        return "\n".join(context_parts)

    def verify_answer(self, answer: str, documents: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Verifies if the answer is faithful to the provided documents."""
        context = self.format_context(documents)
        prompt = CITATION_VERIFICATION_PROMPT.format(context=context, answer=answer)
        
        logger.info("Running citation verification...")
        
        config = types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "is_faithful": {"type": "boolean"},
                    "reasoning": {"type": "string"}
                },
                "required": ["is_faithful", "reasoning"]
            }
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            result = json.loads(response.text)
            return result.get("is_faithful", False), result.get("reasoning", "Failed to parse reasoning.")
            
        except Exception as e:
            logger.error(f"Citation verification failed: {e}")
            return False, str(e)
