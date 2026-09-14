"""
EZChart — global error handler middleware.

Catches all unhandled exceptions and reports politely to user.
Prevents the bot from crashing on edge cases.
"""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.utils.logger import get_logger

log = get_logger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Wrap all handler calls in try/except.

    Logs full traceback, sends a friendly message to user.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            user_id = None
            if isinstance(event, (Message, CallbackQuery)) and event.from_user:
                user_id = event.from_user.id

            log.exception(
                "unhandled_error",
                user_id=user_id,
                error_type=type(e).__name__,
                error=str(e),
            )

            # Try to notify user
            try:
                if isinstance(event, Message):
                    await event.answer(
                        "⚠️ <b>Что-то сломалось на нашей стороне.</b>\n"
                        "Мы уже знаем об ошибке. Попробуй позже."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⚠️ Что-то сломалось. Попробуй позже.",
                        show_alert=True,
                    )
            except Exception:
                # If we can't even reply — just swallow it
                pass

            return None