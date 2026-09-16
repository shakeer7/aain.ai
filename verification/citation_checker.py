import os
import logging
import json
from typing import List, Dict, Any, Tuple
import groq
from llm.prompts import CITATION_VERIFICATION_PROMPT

logger = logging.getLogger(__name__)

class CitationChecker:
    def __init__(self, model_name: str = None):
        self.client = groq.Groq()
        self.model_name = model_name or os.getenv("LLM_MODEL", "llama3-8b-8192")

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        context_parts = []
        for doc in documents:
            source = doc.get("source", "Unknown Source")
            text_en = doc.get("text_en", "")
            context_parts.append(f"[Source: {source}]\n{text_en}\n")
        return "\n".join(context_parts)

    def verify_answer(self, generated_answer: str, retrieved_docs: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Uses an LLM to judge if the generated answer is fully supported by the retrieved documents.
        Returns a tuple of (is_faithful, reasoning).
        """
        if not retrieved_docs:
            return False, "No sources provided for verification."
            
        context = self.format_context(retrieved_docs)
        prompt = CITATION_VERIFICATION_PROMPT.format(
            context=context,
            answer=generated_answer
        )
        
        logger.info("Running citation verification via Groq...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0, # Must be deterministic
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            
            try:
                # Expecting JSON like {"is_faithful": true, "reasoning": "..."}
                result = json.loads(result_text)
                is_faithful = result.get("is_faithful", False)
                reasoning = result.get("reasoning", "No reasoning provided.")
                return is_faithful, reasoning
            except json.JSONDecodeError:
                logger.error(f"Failed to parse verification JSON: {result_text}")
                return False, f"Failed to parse verification response: {result_text}"
                
        except Exception as e:
            logger.error(f"Citation verification failed: {e}")
            return False, str(e)
