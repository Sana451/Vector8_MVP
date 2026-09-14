"""OpenAI LLM provider implementation."""

import json
import logging
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI language model provider."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo") -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-3.5-turbo)
        """
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI provider with model: {model}")

    async def create_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Create a completion using OpenAI API.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools that the model can call

        Returns:
            The response from OpenAI
        """
        try:
            logger.debug(f"Creating completion with OpenAI ({self.model})")

            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**kwargs)

            logger.debug(f"Received response from OpenAI")
            return response

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def get_name(self) -> str:
        """Get the provider name.

        Returns:
            The name 'openai'
        """
        return "openai"

