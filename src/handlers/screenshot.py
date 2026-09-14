"""
EZChart — main screenshot analysis handler (i18n-aware).
"""

import asyncio
import io

from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from PIL import Image

from src.services.ai_client import AIClientError, analyze_chart
from src.utils.image import is_supported_image
from src.utils.logger import get_logger

log = get_logger(__name__)
router = Router(name="screenshot")

TELEGRAM_MAX_LEN = 4000


@router.message(F.photo)
async def handle_photo(
    message: Message, bot: Bot, i18n: I18nContext
) -> None:
    user = message.from_user
    log.info("photo_received", user_id=user.id)

    processing = await message.answer(i18n.get("analysis-in-progress"))

    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)

        buffer = io.BytesIO()
        await bot.download_file(file_info.file_path, buffer)
        image_bytes = buffer.getvalue()

        if not is_supported_image(image_bytes):
            await processing.edit_text(i18n.get("error-unreadable"))
            return

        # Run AI call in thread, pass current locale
        result_text = await asyncio.to_thread(
            _analyze_sync, image_bytes, i18n.locale
        )

        if result_text.startswith("ERROR"):
            await processing.edit_text(i18n.get("error-unreadable"))
            return

        if len(result_text) <= TELEGRAM_MAX_LEN:
            await processing.edit_text(result_text)
        else:
            await processing.edit_text(result_text[:TELEGRAM_MAX_LEN])
            for i in range(TELEGRAM_MAX_LEN, len(result_text), TELEGRAM_MAX_LEN):
                await message.answer(result_text[i : i + TELEGRAM_MAX_LEN])

        log.info("analysis_sent", user_id=user.id, length=len(result_text))

    except AIClientError as e:
        log.error("ai_error", user_id=user.id, error=str(e))
        await processing.edit_text(i18n.get("error-ai-unavailable"))
    except Exception:
        log.exception("unexpected_error", user_id=user.id)
        await processing.edit_text(i18n.get("error-generic"))


def _analyze_sync(image_bytes: bytes, locale: str) -> str:
    """Blocking AI call — executed in a thread."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    normalized_bytes = buf.getvalue()

    return asyncio.run(analyze_chart(normalized_bytes, locale))


@router.message(F.document)
async def handle_document(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("send-as-photo"))


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_fallback(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("send-photo-please"))