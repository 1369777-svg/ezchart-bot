"""
EZChart — application entry point.

Wires up:
- Settings and logging
- Health-check HTTP server (for Render free Web Service)
- Telegram bot + dispatcher
- i18n (Fluent, ru/en/it)
- Handlers (commands, language, screenshot)
- Middlewares (throttling, error handler)

Run: python -m src.main
"""

import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore

from src.config import settings
from src.handlers import commands, language, screenshot
from src.middlewares.error_handler import ErrorHandlerMiddleware
from src.middlewares.i18n_manager import FSMLocaleManager
from src.middlewares.throttling import ThrottlingMiddleware
from src.utils.logger import get_logger, setup_logging

log = get_logger(__name__)


def build_i18n() -> I18nMiddleware:
    """Create i18n middleware with Fluent core + FSM locale manager."""
    core = FluentRuntimeCore(
        path="locales/{locale}/LC_MESSAGES",
        default_locale="en",
    )
    return I18nMiddleware(core=core, manager=FSMLocaleManager())


def build_dispatcher() -> Dispatcher:
    """Create and configure dispatcher with handlers + middlewares."""
    dp = Dispatcher(storage=MemoryStorage())

    # i18n must be registered FIRST so later middlewares/handlers see it
    i18n_middleware = build_i18n()
    i18n_middleware.setup(dp)

    # Error handler catches everything below it
    dp.message.middleware(ErrorHandlerMiddleware())

    # Throttling reads `i18n` from data dict
    dp.message.middleware(ThrottlingMiddleware())

    # Routers (commands first so /start skips throttling)
    dp.include_router(commands.router)
    dp.include_router(language.router)
    dp.include_router(screenshot.router)

    return dp


async def run_health_server(port: int) -> None:
    """
    Minimal HTTP server for Render's health checks.

    Responds with "OK" on GET / and GET /health.
    Render uses this to keep the Web Service awake.
    """
    from aiohttp import web

    async def health(_request: web.Request) -> web.Response:
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    log.info("health_server_started", port=port)


async def main() -> None:
    setup_logging()
    log.info(
        "app_starting",
        model=settings.gemini_model,
        log_level=settings.log_level,
        rate_limit_sec=settings.rate_limit_sec,
    )

    # Start health-check server (for Render free Web Service)
    port = int(os.environ.get("PORT", 8080))
    await run_health_server(port)

    bot = Bot(
        token=settings.telegram_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("bot_polling_started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        log.info("bot_stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("shutdown_by_user")
    except Exception:
        log.exception("fatal_error")
        sys.exit(1)