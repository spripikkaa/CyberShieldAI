"""
In-memory conversation memory store, keyed by conversation_id.
"""

import asyncio
import logging
import time
from collections import deque

logger = logging.getLogger("cybershield.chatbot.conversation_store")

MAX_MESSAGES_PER_CONVERSATION = 10
CONVERSATION_TTL_SECONDS = 60 * 60 * 6


class ConversationStore:
    """Asyncio-safe in-memory store for conversation history."""

    def __init__(self):
        self._store: dict = {}
        self._lock = asyncio.Lock()

    async def get_history(self, conversation_id: str) -> list:
        async with self._lock:
            entry = self._store.get(conversation_id)
            if not entry:
                return []
            return list(entry["messages"])

    async def append(self, conversation_id: str, role: str, text: str) -> None:
        async with self._lock:
            entry = self._store.setdefault(
                conversation_id,
                {
                    "messages": deque(maxlen=MAX_MESSAGES_PER_CONVERSATION),
                    "last_active": time.time(),
                },
            )
            entry["messages"].append({"role": role, "text": text})
            entry["last_active"] = time.time()

    async def clear(self, conversation_id: str) -> bool:
        async with self._lock:
            existed = conversation_id in self._store
            self._store.pop(conversation_id, None)
            return existed

    async def cleanup_expired(self) -> int:
        now = time.time()
        async with self._lock:
            expired = [
                cid
                for cid, entry in self._store.items()
                if now - entry["last_active"] > CONVERSATION_TTL_SECONDS
            ]
            for cid in expired:
                del self._store[cid]
        if expired:
            logger.info("Cleaned up %d expired conversation(s)", len(expired))
        return len(expired)


conversation_store = ConversationStore()
