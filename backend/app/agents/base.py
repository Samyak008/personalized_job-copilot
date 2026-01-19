"""
Pydantic AI Agent Base Configuration

Configures the LLM model provider (OpenRouter) and common agent settings.
"""

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings
from loguru import logger


def get_llm_model(model_name: str = "meta-llama/llama-3.3-70b-instruct:free") -> OpenAIChatModel:
    """
    Get configured LLM model for agents.
    
    Uses OpenRouter as the provider, which gives access to various models
    including free tier options.
    
    Args:
        model_name: The model to use (default: Gemma 2 9B free tier)
        
    Returns:
        OpenAIChatModel configured for OpenRouter
    """
    logger.debug(f"Initializing LLM model: {model_name}")
    
    # Create OpenAI-compatible provider pointing to OpenRouter
    provider = OpenAIProvider(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
    )
    
    return OpenAIChatModel(model_name, provider=provider)


# Common agent configuration
AGENT_RETRIES = 3  # Number of retries for failed agent calls
DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"  # Free tier model


# Alternative models available on OpenRouter (for future use)
AVAILABLE_MODELS = {
    "gemma-3-27b": "google/gemma-3-27b-it:free",  # Free, good for general tasks
    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct:free",  # Free alternative
    "deepseek-r1": "deepseek/deepseek-r1:free",  # Free, reasoning model
}
