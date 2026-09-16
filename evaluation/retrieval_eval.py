import os
import logging
from ragas import evaluate
from ragas.metrics import context_precision, context_recall
from datasets import Dataset
from langchain_groq import ChatGroq
from langchain_core.language_models.llms import BaseLLM
from ragas.llms import LangchainLLMWrapper

logger = logging.getLogger(__name__)

class RetrievalEvaluator:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        # RAGAS natively integrates nicely with Langchain wrappers
        llm = ChatGroq(model=model_name)
        self.ragas_llm = LangchainLLMWrapper(llm)

    def evaluate_retrieval(self, eval_dataset: Dataset) -> dict:
        """
        Evaluates retrieval using Context Precision and Context Recall.
        eval_dataset must have: 'question', 'ground_truth', 'contexts'
        """
        logger.info("Running RAGAS Retrieval Evaluation...")
        
        result = evaluate(
            dataset=eval_dataset,
            metrics=[context_precision, context_recall],
            llm=self.ragas_llm
        )
        
        logger.info(f"Retrieval Evaluation Results: {result}")
        return result
