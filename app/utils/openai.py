import logging

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Get text embedding using OpenAI's embedding models.

    Args:
        text: The text to embed
        model: The embedding model to use (default: text-embedding-3-small)

    Returns:
        List of floats representing the embedding vector

    Raises:
        Exception: If the API call fails
    """
    try:
        response = openai_client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to get embedding for text: {e}")
        raise


def get_embeddings_batch(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """
    Get embeddings for multiple texts in a single API call.

    Args:
        texts: List of texts to embed
        model: The embedding model to use (default: text-embedding-3-small)

    Returns:
        List of embedding vectors, one for each input text

    Raises:
        Exception: If the API call fails
    """
    try:
        response = openai_client.embeddings.create(input=texts, model=model)
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.error(f"Failed to get batch embeddings: {e}")
        raise
