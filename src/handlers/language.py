"""
EZChart — language switching handler (/language).
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.utils.logger import get_logger

log = get_logger(__name__)
router = Router(name="language")

SUPPORTED = ("ru", "en", "it")
LANG_LABELS = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "it": "🇮🇹 Italiano",
}


def _keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code in SUPPORTED:
        kb.button(text=LANG_LABELS[code], callback_data=f"lang:{code}")
    kb.adjust(3)
    return kb.as_markup()


@router.message(Command("language"))
async def cmd_language(message: Message, i18n: I18nContext) -> None:
    await message.answer(
        text=i18n.get("language-prompt"),
        reply_markup=_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def cb_language(callback: CallbackQuery, i18n: I18nContext) -> None:
    lang = callback.data.split(":", 1)[1]
    if lang not in SUPPORTED:
        await callback.answer()
        return

    await i18n.set_locale(lang)
    log.info("language_changed", user_id=callback.from_user.id, lang=lang)

    await callback.message.edit_text(
        text=i18n.get("language-changed"),
        reply_markup=None,
    )
    await callback.answer()