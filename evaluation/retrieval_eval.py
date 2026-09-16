import os
import logging
from ragas import evaluate
from ragas.metrics import context_precision, context_recall
from datasets import Dataset
from langchain_aws import ChatBedrock
from langchain_core.language_models.llms import BaseLLM
from ragas.llms import LangchainLLMWrapper

logger = logging.getLogger(__name__)

class RetrievalEvaluator:
    def __init__(self, model_name: str = None):
        # RAGAS natively integrates nicely with Langchain wrappers
        model = model_name or os.getenv("LLM_MODEL", "meta.llama3-8b-instruct-v1:0")
        llm = ChatBedrock(model_id=model, region_name=os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
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
