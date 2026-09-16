import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in python path
root_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(root_dir))

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from evaluation.datasets import get_sample_evaluation_dataset
from evaluation.retrieval_eval import RetrievalEvaluator
from evaluation.faithfulness import GenerationEvaluator
from retrieval.vector_store import VectorStore
from retrieval.retriever import Retriever
from ingestion.embedder import Embedder
from llm.generator import Generator

def run_pipeline_evaluation():
    logger.info("=== Initializing Components for Evaluation ===")
    embedder = Embedder()
    vector_store = VectorStore()
    retriever = Retriever(vector_store, embedder)
    generator = Generator()
    
    # Load evaluation test set
    eval_dataset = get_sample_evaluation_dataset()
    questions = eval_dataset["question"]
    ground_truths = eval_dataset["ground_truth"]
    
    answers = []
    contexts = []
    
    logger.info(f"Running RAG pipeline for {len(questions)} evaluation queries...")
    for q in questions:
        # Retrieve context
        docs = retriever.retrieve(q, top_k=5)
        doc_texts = [d["text_en"] for d in docs]
        contexts.append(doc_texts)
        
        # Generate answer
        ans = generator.generate_answer(q, docs)
        answers.append(ans)
        
    # Rebuild complete evaluation dataset
    from datasets import Dataset
    full_eval_dataset = Dataset.from_dict({
        "question": questions,
        "ground_truth": ground_truths,
        "answer": answers,
        "contexts": contexts
    })
    
    # 1. Evaluate Retrieval
    logger.info("=== Running Retrieval Evaluation (Context Precision & Recall) ===")
    retrieval_evaluator = RetrievalEvaluator()
    retrieval_metrics = retrieval_evaluator.evaluate_retrieval(full_eval_dataset)
    logger.info(f"Retrieval Metrics: {retrieval_metrics}")
    
    # 2. Evaluate Generation
    logger.info("=== Running Generation Evaluation (Faithfulness & Answer Relevancy) ===")
    generation_evaluator = GenerationEvaluator()
    generation_metrics = generation_evaluator.evaluate_generation(full_eval_dataset)
    logger.info(f"Generation Metrics: {generation_metrics}")
    
    print("\n" + "="*50)
    print("RAGAS EVALUATION REPORT")
    print("="*50)
    print(f"Context Precision : {retrieval_metrics.get('context_precision', 'N/A')}")
    print(f"Context Recall    : {retrieval_metrics.get('context_recall', 'N/A')}")
    print(f"Faithfulness      : {generation_metrics.get('faithfulness', 'N/A')}")
    print(f"Answer Relevancy  : {generation_metrics.get('answer_relevancy', 'N/A')}")
    print("="*50)

if __name__ == "__main__":
    run_pipeline_evaluation()
