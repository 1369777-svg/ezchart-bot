"""
EZChart — FSM-backed locale manager for aiogram-i18n.

Persists user's chosen locale in FSM storage. Falls back to
Telegram's `language_code` if no explicit choice was made.

Compatible with aiogram-i18n 1.x.
"""

from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User
from aiogram_i18n.managers import BaseManager

SUPPORTED_LOCALES = {"ru", "en", "it"}
DEFAULT_LOCALE = "en"


class FSMLocaleManager(BaseManager):
    """Store user's locale choice inside FSM context."""

    async def get_locale(
        self, event: TelegramObject = None, **kwargs: Any
    ) -> str:
        # 1. Explicit user choice (saved in FSM)
        state: FSMContext | None = kwargs.get("state")
        if state is not None:
            user_data = await state.get_data()
            saved = user_data.get("locale")
            if saved in SUPPORTED_LOCALES:
                return saved

        # 2. Telegram's language_code
        user: User | None = kwargs.get("event_from_user")
        if user is not None and user.language_code:
            code = user.language_code.split("-")[0].lower()
            if code in SUPPORTED_LOCALES:
                return code

        # 3. Fallback
        return DEFAULT_LOCALE

    async def set_locale(
        self, locale: str, *args: Any, **kwargs: Any
    ) -> None:
        """Persist chosen locale into FSM state.
        
        Accepts any call signature used by aiogram-i18n 1.x:
        - set_locale(locale, event, **data)
        - set_locale(locale, **data)
        - set_locale(locale=..., **data)
        """
        state: FSMContext | None = kwargs.get("state")
        if state is not None:
            await state.update_data(locale=locale)