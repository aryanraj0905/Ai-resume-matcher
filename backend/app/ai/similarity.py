import logging
import math

from app.ai.embeddings import generate_embedding

logger = logging.getLogger(__name__)


def cosine_similarity(first_vector: list[float], second_vector: list[float]) -> float:
    """
    Calculate cosine similarity between two embedding vectors.

    Cosine similarity measures the angle between two vectors. Values closer to
    1 mean the texts are semantically similar; values closer to 0 mean they are
    less related.
    """
    if len(first_vector) != len(second_vector):
        raise ValueError("Embedding vectors must have the same dimensions.")

    dot_product = sum(
        first_value * second_value
        for first_value, second_value in zip(first_vector, second_vector)
    )
    first_magnitude = math.sqrt(
        sum(first_value * first_value for first_value in first_vector)
    )
    second_magnitude = math.sqrt(
        sum(second_value * second_value for second_value in second_vector)
    )

    if first_magnitude == 0 or second_magnitude == 0:
        return 0.0

    return dot_product / (first_magnitude * second_magnitude)


def calculate_semantic_similarity(resume_text: str, job_description: str) -> float:
    """
    Compare resume text and job description using sentence embeddings.

    Args:
        resume_text: Full resume text extracted from the uploaded PDF.
        job_description: Full job description provided by the user.

    Returns:
        A percentage score from 0.0 to 100.0.
    """
    logger.info("Generating semantic similarity score.")

    resume_embedding = generate_embedding(resume_text)
    job_embedding = generate_embedding(job_description)
    similarity = cosine_similarity(resume_embedding, job_embedding)

    bounded_similarity = max(0.0, min(similarity, 1.0))
    return round(bounded_similarity * 100, 2)
