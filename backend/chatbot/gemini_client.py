import logging
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("cybershield.chatbot.gemini_client")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("GROQ_TIMEOUT_SECONDS", "20")
)


class GeminiClientError(Exception):
    pass


class GeminiAuthError(GeminiClientError):
    pass


class GeminiRequestError(GeminiClientError):
    pass


class GeminiResponseError(GeminiClientError):
    pass


class GeminiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or DEFAULT_MODEL

        if not self.api_key:
            raise GeminiAuthError(
                "GROQ_API_KEY is missing. Add it to the project .env file."
            )

    async def generate(
        self,
        system_prompt: str,
        history: list,
        user_message: str,
        temperature: float = 0.3,
        max_output_tokens: int = 400,
    ) -> str:
        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        for turn in history:
            role = turn.get("role")
            text = turn.get("text", "")

            if role == "model":
                role = "assistant"

            if role in ("user", "assistant") and text:
                messages.append(
                    {
                        "role": role,
                        "content": text,
                    }
                )

        current_question = f"""
IMPORTANT — CURRENT USER QUESTION:

{user_message}

Answer ONLY the current user question above.

Use previous conversation messages ONLY when they are necessary
to understand the current question.

Do NOT repeat previous answers.
Do NOT summarize the previous conversation.
Do NOT answer previous questions again.
Do NOT combine multiple previous answers with the current answer.

If the current question is a simple question, give a short answer.
For "how to use" questions, give short numbered steps.
For cybersecurity definitions, give a simple 1-3 sentence explanation.
For CyberShield AI application questions, answer specifically about
the CyberShield AI application.

The current question has the highest priority.
"""

        messages.append(
            {
                "role": "user",
                "content": current_question,
            }
        )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT_SECONDS
            ) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json=payload,
                )

        except httpx.TimeoutException as exc:
            raise GeminiRequestError(
                "AI service timeout"
            ) from exc

        except httpx.RequestError as exc:
            raise GeminiRequestError(
                "Could not connect to AI service"
            ) from exc

        if response.status_code in (401, 403):
            logger.error(response.text)
            raise GeminiAuthError(
                "Groq authentication failed. Check GROQ_API_KEY."
            )

        if response.status_code == 429:
            raise GeminiRequestError(
                "Groq rate limit reached. Try again later."
            )

        if response.status_code >= 400:
            logger.error(response.text)
            raise GeminiRequestError(
                f"Groq error {response.status_code}"
            )

        try:
            data = response.json()

            text = (
                data["choices"][0]
                ["message"]
                ["content"]
            )

            return text.strip()

        except Exception as exc:
            logger.error(
                "Invalid Groq response: %s",
                response.text,
            )
            raise GeminiResponseError(
                "Invalid AI response"
            ) from exc
