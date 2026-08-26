"""FastAPI router for the CyberShield AI chatbot."""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.chatbot.chat_service import ChatService, ChatServiceError
from backend.chatbot.gemini_client import (
    GeminiAuthError,
    GeminiClientError,
    GeminiRequestError,
    GeminiResponseError,
)

logger = logging.getLogger("cybershield.chatbot.routes")

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

_chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


class ScanResultPayload(BaseModel):
    prediction: str = Field(..., description="e.g. 'Phishing' or 'Legitimate'")
    reasons: list = Field(default_factory=list)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    url: Optional[str] = None


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(
        default=None,
        description="Session identifier. If omitted, a new one is generated.",
    )
    message: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Free-form user message",
    )
    scan_result: Optional[ScanResultPayload] = Field(
        default=None,
        description="Structured scan result for scan explanations.",
    )


class ChatResponse(BaseModel):
    reply: str
    is_scan_explanation: bool
    conversation_id: str


class ClearResponse(BaseModel):
    cleared: bool
    conversation_id: str


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Send a message or scan result to the CyberShield AI chatbot",
)
async def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid.uuid4())

    if not request.message and not request.scan_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'message' or 'scan_result' must be provided.",
        )

    scan_dict = request.scan_result.model_dump() if request.scan_result else None

    try:
        result = await get_chat_service().get_response(
            conversation_id=conversation_id,
            message=request.message,
            scan_result=scan_dict,
        )
        return ChatResponse(**result)

    except ChatServiceError as exc:
        logger.warning("Chat validation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except GeminiAuthError as exc:
        logger.critical("Groq auth misconfigured: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Chatbot service is temporarily unavailable. "
                "Please try again later."
            ),
        ) from exc

    except (GeminiRequestError, GeminiResponseError, GeminiClientError) as exc:
        logger.error("Groq upstream error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc) or "The AI service failed to respond. Please try again.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error in /chatbot/chat: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc


@router.delete(
    "/chat/{conversation_id}",
    response_model=ClearResponse,
    summary="Clear a conversation's server-side memory",
)
async def clear_chat(conversation_id: str) -> ClearResponse:
    try:
        cleared = await get_chat_service().clear_conversation(conversation_id)
        return ClearResponse(cleared=cleared, conversation_id=conversation_id)
    except Exception as exc:
        logger.exception(
            "Error clearing conversation %s: %s",
            conversation_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation.",
        ) from exc


@router.get("/health", summary="Chatbot module health check")
async def health_check() -> dict:
    return {"status": "ok", "module": "chatbot"}
