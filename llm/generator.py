import os
import logging
from typing import List, Dict, Any
import groq
from llm.prompts import RAG_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, model_name: str = None):
        """Initializes the LLM Generator using the official Groq SDK."""
        self.client = groq.Groq()
        self.model_name = model_name or os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

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
        
        logger.info(f"Calling {self.model_name} for generation via Groq...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                top_p=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "An error occurred during generation."
