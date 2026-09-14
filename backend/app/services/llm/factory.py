"""LLM provider factory for selecting and creating providers."""

import logging
from typing import Literal

from app.services.llm.base import LLMProvider
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

LLMProviderType = Literal["openai", "groq"]


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create_provider(
        provider_name: LLMProviderType,
        api_key: str,
        model: str | None = None,
    ) -> LLMProvider:
        """Create an LLM provider instance.

        Args:
            provider_name: Name of the provider ('openai' or 'groq')
            api_key: API key for the provider
            model: Optional model name (uses default if not provided)

        Returns:
            An instance of the requested LLM provider

        Raises:
            ValueError: If the provider name is not recognized
            ValueError: If the API key is missing
        """
        logger.info(f"Creating LLM provider: {provider_name}")

        if provider_name == "openai":
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return OpenAIProvider(
                api_key=api_key,
                model=model or "gpt-3.5-turbo",
            )

        elif provider_name == "groq":
            if not api_key:
                raise ValueError("GROQ_API_KEY is required for Groq provider")
            return GroqProvider(
                api_key=api_key,
                model=model or "groq/compound-mini",
            )

        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available providers.

        Returns:
            List of available provider names
        """
        return ["openai", "groq"]





