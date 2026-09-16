import os
import logging
import json
from typing import List, Dict, Any, Tuple
import boto3
from llm.prompts import CITATION_VERIFICATION_PROMPT

logger = logging.getLogger(__name__)

class CitationChecker:
    def __init__(self, model_name: str = None):
        self.client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
        self.model_name = model_name or os.getenv("LLM_MODEL", "meta.llama3-8b-instruct-v1:0")

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
        
        logger.info("Running citation verification via AWS Bedrock...")
        
        try:
            # Enforce JSON output in the prompt itself since Bedrock raw API doesn't have a response_format toggle
            json_prompt = prompt + "\n\nRespond ONLY with a valid JSON object matching this schema: {\"is_faithful\": boolean, \"reasoning\": \"string\"}"
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{json_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            request_body = {
                "prompt": formatted_prompt,
                "max_gen_len": 512,
                "temperature": 0.0,
                "top_p": 0.8
            }
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            result_text = response_body.get('generation', '')
            
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
