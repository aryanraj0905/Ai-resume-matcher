import logging
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> Any:
    """
    Load and cache the sentence-transformer model for the current process.

    Sentence Transformer models are expensive to initialize, so this function
    must be the only place that loads the model. The lru_cache ensures the
    model is created once and then reused for later requests.
    """
    logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a dense vector embedding for a text document.

    Args:
        text: Resume text, job description text, or another document string.

    Returns:
        A list of floats representing the text's semantic meaning.
    """
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("Cannot generate an embedding for empty text.")

    model = get_embedding_model()
    embedding = model.encode(cleaned_text, convert_to_numpy=True)

    return embedding.astype(float).tolist()
