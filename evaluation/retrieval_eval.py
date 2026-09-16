import logging
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

class RetrievalEvaluator:
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        # RAGAS natively integrates nicely with Langchain wrappers
        llm = ChatGoogleGenerativeAI(model=model_name)
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
