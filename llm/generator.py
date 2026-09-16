import os
import logging
from typing import List, Dict, Any
import boto3
import json
from llm.prompts import RAG_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, model_name: str = None):
        """Initializes the LLM Generator using AWS Bedrock."""
        self.client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
        self.model_name = model_name or os.getenv("LLM_MODEL", "meta.llama3-8b-instruct-v1:0")

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
        
        logger.info(f"Calling {self.model_name} for generation via AWS Bedrock...")
        
        try:
            # Format request for Llama 3 on Bedrock
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            
            request_body = {
                "prompt": formatted_prompt,
                "max_gen_len": 1024,
                "temperature": 0.1,
                "top_p": 0.8
            }
            
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('generation', '')
            
        except Exception as e:
            logger.error(f"Error during LLM generation via Bedrock: {e}")
            return "An error occurred while generating the response."
