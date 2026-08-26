"""Business logic layer for the CyberShield AI Chatbot."""

import logging
import re
from typing import Optional

from backend.chatbot.conversation_store import conversation_store
from backend.chatbot.gemini_client import (
    GeminiAuthError,
    GeminiClient,
    GeminiClientError,
    GeminiRequestError,
    GeminiResponseError,
)
from backend.chatbot.system_prompt import (
    SYSTEM_PROMPT,
    format_structured_scan_result,
)

logger = logging.getLogger("cybershield.chatbot.chat_service")

SCAN_RESULT_PATTERN = re.compile(r"prediction\s*:\s*.+", re.IGNORECASE)

MAX_MESSAGE_LENGTH = 2000


class ChatServiceError(Exception):
    """Raised for validation or orchestration failures within chat_service."""


class ChatService:
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self._client = gemini_client or GeminiClient()

    async def get_response(
        self,
        conversation_id: str,
        message: Optional[str] = None,
        scan_result: Optional[dict] = None,
    ) -> dict:
        if not conversation_id:
            raise ChatServiceError("conversation_id is required.")

        is_scan = False

        if scan_result:
            formatted = format_structured_scan_result(scan_result)
            effective_message = self._wrap_scan_instruction(formatted)
            display_message = formatted
            is_scan = True
        else:
            text = (message or "").strip()
            if not text:
                raise ChatServiceError("Message cannot be empty.")
            if len(text) > MAX_MESSAGE_LENGTH:
                logger.warning(
                    "Message rejected: exceeds max length (%d chars)",
                    len(text),
                )
                raise ChatServiceError(
                    f"Message is too long. Please keep it under "
                    f"{MAX_MESSAGE_LENGTH} characters."
                )

            is_scan = self._is_plain_text_scan(text)
            effective_message = (
                self._wrap_scan_instruction(text) if is_scan else text
            )
            display_message = text

        history = await conversation_store.get_history(conversation_id)

        logger.info(
            "Processing chat request | conversation_id=%s | scan_mode=%s | "
            "history_len=%d",
            conversation_id,
            is_scan,
            len(history),
        )

        try:
            reply = await self._client.generate(
                system_prompt=SYSTEM_PROMPT,
                history=history,
                user_message=effective_message,
            )
        except GeminiAuthError:
            logger.error("Groq auth error — check GROQ_API_KEY configuration.")
            raise
        except GeminiRequestError:
            logger.error("Groq request failed (network/HTTP).")
            raise
        except GeminiResponseError:
            logger.error("Groq returned malformed/empty response.")
            raise
        except GeminiClientError:
            logger.error("Unclassified Groq client error.")
            raise

        await conversation_store.append(conversation_id, "user", display_message)
        await conversation_store.append(conversation_id, "model", reply)

        logger.info(
            "Chat response generated | conversation_id=%s | reply_len=%d",
            conversation_id,
            len(reply),
        )

        return {
            "reply": reply,
            "is_scan_explanation": is_scan,
            "conversation_id": conversation_id,
        }

    async def clear_conversation(self, conversation_id: str) -> bool:
        cleared = await conversation_store.clear(conversation_id)
        logger.info(
            "Conversation cleared | conversation_id=%s | existed=%s",
            conversation_id,
            cleared,
        )
        return cleared

    @staticmethod
    def _is_plain_text_scan(message: str) -> bool:
        return bool(SCAN_RESULT_PATTERN.search(message)) and "reason" in message.lower()

    @staticmethod
    def _wrap_scan_instruction(formatted_scan_text: str) -> str:
        return (
            "The following is a phishing scan result from CyberShield AI. "
            "Please explain it to the user following the scan result explanation "
            "format defined in your instructions:\n\n"
            f"{formatted_scan_text.strip()}"
        )
