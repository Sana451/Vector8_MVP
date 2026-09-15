"""Routes for AI chat with tool calling."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser
from app.core.rate_limit import chat_rate_limiter
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    history: list[dict[str, str]] | None = Field(
        default=None, description="Previous messages in conversation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Calculate the route from Dallas to Houston for me",
                "history": [],
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="AI assistant response")


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(current_user: CurrentUser, request: ChatRequest) -> Any:
    """Process a chat message with AI assistance.

    The AI can calculate routes by calling the calculate_route tool.
    Coordinates should be provided as latitude and longitude values.

    Args:
        current_user: Authenticated user
        request: Chat request with user message and optional history

    Returns:
        ChatResponse with AI response text

    Raises:
        HTTPException: If OpenAI API is not configured or API call fails
    """
    chat_rate_limiter.check(str(current_user.id))

    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")

        # Initialize chat service
        chat_service = ChatService()

        # Process the message
        response_text = await chat_service.process_chat_message(
            user_input=request.message, history=request.history
        )

        logger.info("Chat request processed successfully")

        return ChatResponse(response=response_text)

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Configuration error: {error_msg}")

        if "not configured" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service is not properly configured: {error_msg}. "
                       "Please ensure the required API key is set in .env file "
                       "and configure LLM_PROVIDER appropriately.",
            ) from e

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration error: {error_msg}",
        ) from e

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing chat: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message. Please try again.",
        ) from e

