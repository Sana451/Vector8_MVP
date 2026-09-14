"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for Language Model providers."""

    @abstractmethod
    async def create_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Create a completion using the LLM provider.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools that the LLM can call

        Returns:
            The response from the LLM provider
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the provider name.

        Returns:
            The name of the provider (e.g., 'openai', 'groq')
        """
        pass

