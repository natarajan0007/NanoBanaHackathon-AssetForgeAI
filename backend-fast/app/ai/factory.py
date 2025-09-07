from .base import AIProvider
from .gemini_provider import GeminiProvider
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    """Factory function to get the configured AI provider"""
    if settings.AI_PROVIDER == "gemini":
        return GeminiProvider(api_key=settings.GEMINI_API_KEY)
    else:
        raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")
