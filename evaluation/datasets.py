from datasets import Dataset

def get_sample_evaluation_dataset() -> Dataset:
    """
    Returns a sample evaluation dataset formatted for RAGAS.
    In a real MLOps pipeline, this would be loaded from a robust test set (e.g., in a DVC or HuggingFace repo).
    """
    data = {
        "question": [
            "What are the pillars of Islam?",
            "What does the Quran say about patience?"
        ],
        "ground_truth": [
            "The pillars of Islam are five: Testifying that there is no god but Allah and that Muhammad is the Messenger of Allah, establishing the prayer, paying the zakat, fasting Ramadan, and the pilgrimage to the House.",
            "The Quran mentions that God is with those who are patient."
        ],
        "answer": [
            # Populated during the evaluation pipeline run
        ],
        "contexts": [
            # Populated during the evaluation pipeline run
        ]
    }
    
    return Dataset.from_dict(data)
