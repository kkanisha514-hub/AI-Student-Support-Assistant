"""
Local LLM integration: Gemma served through Ollama.
No API key or cloud dependency required.
"""
from functools import lru_cache
from langchain_ollama import ChatOllama
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.2) -> ChatOllama:
    """
    Returns a cached ChatOllama instance pointing at the local Ollama server.
    Make sure `ollama serve` is running and the model has been pulled, e.g.:
        ollama pull qwen2.5:3b
    """
    logger.info(f"Initializing Gemma via Ollama: model={settings.GEMMA_MODEL}")
    return ChatOllama(
        model=settings.GEMMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature,
    )
