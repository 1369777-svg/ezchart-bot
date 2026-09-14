"""
EZChart — basic command handlers: /start, /help, /about.
"""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_i18n import I18nContext

from src.utils.logger import get_logger

log = get_logger(__name__)
router = Router(name="commands")


@router.message(CommandStart())
async def cmd_start(message: Message, i18n: I18nContext) -> None:
    user = message.from_user
    log.info("user_started", user_id=user.id, username=user.username)
    await message.answer(i18n.get("start-message"))


@router.message(Command("help"))
async def cmd_help(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("help-message"))


@router.message(Command("about"))
async def cmd_about(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("about-message"))