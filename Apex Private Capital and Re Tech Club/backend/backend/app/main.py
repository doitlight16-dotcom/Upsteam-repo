"""Application entry point and composition root.

This is the one place allowed to know about every layer at once: it reads
configuration, configures logging, and wires middleware and routers
together. Nothing downstream should need to reach back up into this
module.

Deliberately NOT yet included, pending their own build steps:
  - Database engine lifecycle (asyncpg pool startup/shutdown)
  - Tenant-context middleware + Row-Level Security session binding
  - Auth routes (Telegram initData verification, JWT issuance)
  - AI module client wiring

Adding those should only ever mean adding a few lines to `create_app()`
and `lifespan()` below -- if it requires touching domain or application
code, something about the layering has leaked.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.schedule import router as schedule_router
from app.api.v1.routers.participants import router as participants_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware.request_id import RequestIdMiddleware
from app.infrastructure.db import sessionmanager, Base
from app.domain.models import * # Import models to register them with Base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)
    logger.info(
        "application_starting",
        environment=settings.environment.value,
        debug=settings.debug,
    )
    
    # Initialize DB Connection
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/appex")
    sessionmanager.init(db_url)
    
    # Create tables automatically for MVP deployment
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start Telegram Bot polling in background
    bot_task = None
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
    if bot_token:
        try:
            from app.bot.bot import start_bot
            bot_task = asyncio.create_task(start_bot())
            logger.info("telegram_bot_background_task_created")
        except Exception as e:
            logger.error("telegram_bot_failed_to_start", error=str(e))

    yield

    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except (asyncio.CancelledError, Exception):
            pass

    await sessionmanager.close()
    logger.info("application_stopping")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application instance.

    Accepting an optional `settings` override (rather than always calling
    `get_settings()` internally) is what makes this factory usable from
    tests without mutating environment variables.
    """
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(schedule_router, prefix=settings.api_v1_prefix)
    app.include_router(participants_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
