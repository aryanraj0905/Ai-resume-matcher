import logging
from functools import lru_cache
from typing import Any

from app.config import ENABLE_SEMANTIC_MATCHING

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingModelUnavailable(RuntimeError):
    """Raised when the semantic embedding model is not available locally."""


@lru_cache(maxsize=1)
def get_embedding_model() -> Any:
    """
    Load and cache the sentence-transformer model for the current process.

    Sentence Transformer models are expensive to initialize, so this function
    must be the only place that loads the model. The lru_cache ensures the
    model is created once and then reused for later requests.

    This is also the single gate for ENABLE_SEMANTIC_MATCHING: every embedding
    consumer (semantic similarity, and the experience/education/projects
    category scorers' semantic fallback) goes through here, so disabling the
    flag skips loading torch/sentence-transformers entirely rather than just
    turning off the standalone semantic_similarity category.
    """
    if not ENABLE_SEMANTIC_MATCHING:
        raise EmbeddingModelUnavailable(
            "Semantic matching is disabled (ENABLE_SEMANTIC_MATCHING=false)."
        )

    logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)

    from sentence_transformers import SentenceTransformer

    try:
        # Prefer an already-cached model (fast, works offline in production),
        # but fall back to downloading it the first time it is needed.
        return SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
    except Exception:
        try:
            return SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception as exc:
            raise EmbeddingModelUnavailable(
                "Embedding model could not be loaded or downloaded. Check "
                "internet access on first run, or disable semantic matching."
            ) from exc


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
