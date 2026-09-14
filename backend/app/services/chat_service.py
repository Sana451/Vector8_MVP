"""Chat service for AI-powered conversation with tool calling."""

import json
import logging
from typing import Any

from app.core.config import settings
from app.services.llm.factory import LLMProviderFactory
from app.services.llm.base import LLMProvider
from app.tools.route_tools import calculate_route_tool, get_calculate_route_tool_schema

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing AI chat with tool calling capabilities."""

    def __init__(self) -> None:
        """Initialize the chat service with the configured LLM provider."""
        # Get the LLM provider from config
        provider_name = settings.LLM_PROVIDER.lower()

        logger.info(f"Initializing ChatService with LLM provider: {provider_name}")

        # Select API key based on provider
        if provider_name == "openai":
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not configured")
        elif provider_name == "groq":
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY is not configured")
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

        # Create the provider instance
        self.provider: LLMProvider = LLMProviderFactory.create_provider(
            provider_name=provider_name,  # type: ignore
            api_key=api_key,
            model=settings.LLM_MODEL,
        )

        logger.info(f"ChatService initialized with {self.provider.get_name()} provider")

    async def process_chat_message(
        self, user_input: str, history: list[dict[str, str]] | None = None
    ) -> str:
        """Process a chat message with tool calling support.

        Args:
            user_input: The user's input message
            history: Optional list of previous messages in the conversation

        Returns:
            The final response from the AI

        Raises:
            ValueError: If LLM provider is not configured
        """
        # Initialize history if not provided
        if history is None:
            history = []

        # Build messages list
        messages = history.copy()
        messages.append({"role": "user", "content": user_input})

        logger.info(
            f"Processing chat message with {self.provider.get_name()}: {user_input[:100]}..."
        )

        try:
            # First API call: get initial response with possible tool calls
            response = await self.provider.create_completion(
                messages=messages,
                tools=[get_calculate_route_tool_schema()],
            )

            # Check if there are tool calls to handle
            if response.choices[0].message.tool_calls:
                logger.info(
                    f"Tool calls detected: {len(response.choices[0].message.tool_calls)}"
                )

                # Process each tool call
                tool_results = await self._handle_tool_calls(
                    response.choices[0].message.tool_calls
                )

                # Add assistant message to history with tool_calls
                assistant_message: dict[str, Any] = {
                    "role": "assistant",
                    "content": response.choices[0].message.content or "",
                }

                # Include tool_calls in the assistant message if present
                if response.choices[0].message.tool_calls:
                    assistant_message["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in response.choices[0].message.tool_calls
                    ]

                messages.append(assistant_message)

                # Add tool results to history
                for tool_result in tool_results:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_result["tool_call_id"],
                            "content": tool_result["content"],
                        }
                    )

                # Get final response from AI
                final_response = await self.provider.create_completion(
                    messages=messages,
                )

                final_text = final_response.choices[0].message.content or ""
                logger.info("Chat message processed successfully with tool calls")
                return final_text

            else:
                # No tool calls, return the response directly
                final_text = response.choices[0].message.content or ""
                logger.info("Chat message processed successfully without tool calls")
                return final_text

        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            raise

    async def _handle_tool_calls(
        self, tool_calls: list[Any]
    ) -> list[dict[str, str]]:
        """Handle tool calls from the AI model.

        Args:
            tool_calls: List of tool calls from the LLM

        Returns:
            List of tool results with tool_call_id and content
        """
        tool_results = []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

            try:
                if tool_name == "calculate_route":
                    result = await calculate_route_tool(
                        start_lat=tool_args["start_lat"],
                        start_lon=tool_args["start_lon"],
                        end_lat=tool_args["end_lat"],
                        end_lon=tool_args["end_lon"],
                    )
                    content = json.dumps(result)
                else:
                    content = json.dumps({"error": f"Unknown tool: {tool_name}"})

            except ValueError as e:
                logger.warning(f"Validation error for tool {tool_name}: {e}")
                content = json.dumps({"error": f"Invalid parameters: {str(e)}"})
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                content = json.dumps({"error": f"Tool execution failed: {str(e)}"})

            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "content": content,
                }
            )

        return tool_results

