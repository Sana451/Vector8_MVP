"""Groq LLM provider implementation."""

import json
import logging
from typing import Any

from groq import AsyncGroq

from app.services.llm.base import LLMProvider
from app.tools.route_tools import convert_tools_to_groq_format

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Groq language model provider."""

    def __init__(self, api_key: str, model: str = "groq/compound-mini") -> None:
        """Initialize Groq provider.

        Args:
            api_key: Groq API key
            model: Model name (default: groq/compound-mini)
        """
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for Groq provider")

        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Groq provider with model: {model}")

    async def create_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Create a completion using Groq API.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools that the model can call (Groq supports tool_use)

        Returns:
            The response from Groq
        """
        try:
            logger.debug(f"Creating completion with Groq ({self.model})")
            logger.debug(f"Messages: {json.dumps(messages, indent=2)}")

            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
            }

            if tools:
                # Convert tools to Groq format
                groq_tools = convert_tools_to_groq_format(tools)

                if groq_tools:
                    # Validate tools before sending
                    for tool in groq_tools:
                        if tool.get("type") != "function":
                            logger.warning(f"Tool has invalid type: {tool}")
                            continue
                        if "function" not in tool:
                            logger.warning(f"Tool missing function field: {tool}")
                            continue
                        func = tool["function"]
                        if not func.get("name"):
                            logger.error(f"Tool function missing name: {func}")
                            continue

                    kwargs["tools"] = groq_tools
                    kwargs["tool_choice"] = "auto"
                    logger.info(f"Sending {len(groq_tools)} tools to Groq")
                    for tool in groq_tools:
                        tool_name = tool.get("function", {}).get("name", "unknown")
                        logger.debug(f"  - Tool: {tool_name}")
                else:
                    logger.warning("No valid tools to send to Groq after conversion")

            response = await self.client.chat.completions.create(**kwargs)

            logger.debug(f"Received response from Groq")
            return response

        except Exception as e:
            logger.error(f"Groq API error: {e}", exc_info=True)
            raise

    def get_name(self) -> str:
        """Get the provider name.

        Returns:
            The name 'groq'
        """
        return "groq"





