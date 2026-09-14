"""
EZChart — throttling middleware.

Prevents spam: one message per user per N seconds.
Configurable via RATE_LIMIT_SEC env var.
"""

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from src.config import settings
from src.utils.logger import get_logger

log = get_logger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple in-memory rate limiter.

    Key: user_id.
    Window: settings.rate_limit_sec seconds.

    For MVP — in-memory dict is fine. For scale:
    swap to Redis-backed storage (RedisStorage).
    """

    def __init__(self, window_sec: int | None = None) -> None:
        self.window_sec = window_sec or settings.rate_limit_sec
        self._last_seen: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Only throttle messages; skip other event types
        if not isinstance(event, Message):
            return await handler(event, data)

        # Skip commands — they're cheap and important for UX
        if event.text and event.text.startswith("/"):
            return await handler(event, data)

        user = event.from_user
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_seen.get(user.id, 0.0)
        elapsed = now - last

        if elapsed < self.window_sec:
            wait = int(self.window_sec - elapsed) + 1
            log.info(
                "throttled",
                user_id=user.id,
                elapsed=round(elapsed, 1),
                wait=wait,
            )
            await event.answer(
                f"⏳ <b>Слишком быстро.</b>\n"
                f"Подожди <b>{wait} сек</b> перед следующим анализом."
            )
            return None

        self._last_seen[user.id] = now
        return await handler(event, data)