import os
import logging
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
)
from ragas.llms import LangchainLLMWrapper
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

class GenerationEvaluator:
    def __init__(self, model_name: str = None):
        model = model_name or os.getenv("LLM_MODEL", "llama3-8b-8192")
        llm = ChatGroq(model=model)
        self.ragas_llm = LangchainLLMWrapper(llm)

    def evaluate_generation(self, eval_dataset: Dataset) -> dict:
        """
        Evaluates generation using Faithfulness and Answer Relevancy.
        eval_dataset must have: 'question', 'answer', 'contexts'
        """
        logger.info("Running RAGAS Generation Evaluation...")
        
        result = evaluate(
            dataset=eval_dataset,
            metrics=[faithfulness, answer_relevancy],
            llm=self.ragas_llm
        )
        
        logger.info(f"Generation Evaluation Results: {result}")
        return result
