import os
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from llm.prompts import RAG_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, model_name: str = None):
        """Initializes the LLM Generator using the official Google GenAI SDK."""
        self.client = genai.Client()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        context_parts = []
        for doc in documents:
            source = doc.get("source", "Unknown Source")
            text_en = doc.get("text_en", "")
            context_parts.append(f"[Source: {source}]\n{text_en}\n")
        return "\n".join(context_parts)

    def generate_answer(self, question: str, documents: List[Dict[str, Any]]) -> str:
        context = self.format_context(documents)
        prompt = RAG_SYSTEM_PROMPT.format(context=context, question=question)
        
        logger.info(f"Calling {self.model_name} for generation...")
        
        # We can configure the model to be deterministic and grounded
        config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.8,
            max_output_tokens=1024,
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "An error occurred during generation."
