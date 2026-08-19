"""APEX ASSET SUITE — Vercel Serverless Entry Point
====================================================
Архитектура: Telegram Webhook + FastAPI + Mangum (ASGI → Serverless)

Поток запросов:
  POST /api/webhook    ← Telegram шлёт сюда каждое сообщение/callback
  GET  /api/setup      ← Вызвать ОДИН РАЗ после деплоя для регистрации вебхука
  GET  /api/health     ← Мониторинг состояния

Безопасность:
  - Webhook защищён заголовком X-Telegram-Bot-Api-Secret-Token
  - FSM состояния хранятся в Upstash Redis (переживают перезапуск функции)
"""

from __future__ import annotations

import hmac
import logging
import os
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update

# dotenv для локальной разработки
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# КОНФИГУРАЦИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.critical("❌ BOT_TOKEN не задан! Задайте переменную окружения в Vercel Dashboard.")
    # Не делаем sys.exit() — на Vercel это убьёт весь деплой при импорте.
    # Вместо этого эндпоинты вернут 500 при попытке использовать бота.

WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
VERCEL_URL: str = os.getenv("VERCEL_URL", "").rstrip("/")
UPSTASH_REDIS_URL: str = os.getenv("UPSTASH_REDIS_URL") or os.getenv("REDIS_URL", "")
ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "https://appex-adipec-concierge.vercel.app")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ИНИЦИАЛИЗАЦИЯ AIOGRAM (один раз при холодном старте)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_dispatcher() -> Dispatcher:
    """Создаёт Dispatcher с Redis или Memory storage."""
    if UPSTASH_REDIS_URL:
        try:
            storage = RedisStorage.from_url(UPSTASH_REDIS_URL)
            logger.info("✅ FSM Storage: Upstash Redis")
            return Dispatcher(storage=storage)
        except Exception as e:
            logger.warning("Redis init failed (%s), falling back to MemoryStorage", e)

    from aiogram.fsm.storage.memory import MemoryStorage
    logger.warning(
        "⚠️ FSM Storage: MemoryStorage (НЕ ПОДХОДИТ для Serverless — FSM сбросится при каждом запросе). "
        "Задайте UPSTASH_REDIS_URL."
    )
    return Dispatcher(storage=MemoryStorage())


bot = Bot(
    token=BOT_TOKEN or "placeholder:placeholder",  # placeholder если токен не задан
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = _build_dispatcher()

# Регистрируем все хендлеры из bot/handlers.py
# Импорт после инициализации bot/dp чтобы избежать circular imports
from bot.handlers import build_router  # noqa: E402
dp.include_router(build_router())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASTAPI ПРИЛОЖЕНИЕ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="APEX ASSET SUITE — Bot API",
    description="Telegram Webhook + Web App API для ADIPEC Concierge",
    version="2.0.0",
    docs_url=None,   # Отключаем Swagger UI в продакшене
    redoc_url=None,
)

# CORS — разрешаем только домен WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ЭНДПОИНТЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/api/webhook")
async def telegram_webhook(request: Request) -> dict:
    """
    Telegram шлёт сюда POST-запрос при каждом сообщении/callback.

    Безопасность:
      - Проверяем X-Telegram-Bot-Api-Secret-Token (если WEBHOOK_SECRET задан)
      - Если токен не совпадает → 401 Unauthorized
    """
    # ── Валидация секретного токена ──
    if WEBHOOK_SECRET:
        incoming_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(incoming_secret, WEBHOOK_SECRET):
            logger.warning("Webhook: неверный секретный токен — запрос отклонён.")
            raise HTTPException(status_code=401, detail="Unauthorized")

    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")

    # ── Парсим Update и передаём в Dispatcher ──
    try:
        body = await request.json()
        update = Update.model_validate(body, context={"bot": bot})
        await dp.feed_update(bot=bot, update=update)
        return {"ok": True}
    except Exception as e:
        logger.exception("Webhook processing error: %s", e)
        # Важно: возвращаем 200 даже при ошибке обработки,
        # иначе Telegram будет повторно присылать тот же Update.
        return {"ok": False, "error": str(e)}


@app.get("/api/setup")
async def setup_webhook() -> dict:
    """
    Регистрирует вебхук в Telegram.
    Вызовите ОДИН РАЗ после деплоя:
      GET https://your-project.vercel.app/api/setup

    После успешной регистрации этот эндпоинт можно не трогать.
    """
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")
    if not VERCEL_URL:
        raise HTTPException(
            status_code=500,
            detail="VERCEL_URL not configured. Set it in Vercel Environment Variables."
        )

    webhook_url = f"{VERCEL_URL}/api/webhook"

    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET or None,
            allowed_updates=["message", "callback_query", "inline_query"],
            drop_pending_updates=True,  # Игнорируем накопившиеся сообщения
        )
        info = await bot.get_webhook_info()
        logger.info("Webhook set: %s", webhook_url)
        return {
            "ok": True,
            "webhook_url": webhook_url,
            "pending_updates": info.pending_update_count,
            "secret_configured": bool(WEBHOOK_SECRET),
        }
    except Exception as e:
        logger.exception("set_webhook failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/setup")
async def delete_webhook() -> dict:
    """Удаляет вебхук (полезно при переезде или для отладки)."""
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        return {"ok": True, "message": "Webhook deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check() -> dict:
    """Health check для мониторинга."""
    webhook_configured = False
    if BOT_TOKEN:
        try:
            info = await bot.get_webhook_info()
            webhook_configured = bool(info.url)
        except Exception:
            pass

    return {
        "status": "ok",
        "service": "APEX ASSET SUITE Bot",
        "version": "2.0.0",
        "bot_token_set": bool(BOT_TOKEN),
        "webhook_secret_set": bool(WEBHOOK_SECRET),
        "redis_configured": bool(UPSTASH_REDIS_URL),
        "webhook_configured": webhook_configured,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERCEL SERVERLESS HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Vercel ищет переменную `handler` в файле и вызывает её.
# Mangum превращает FastAPI ASGI-приложение в AWS Lambda / Vercel совместимый хендлер.
handler = Mangum(app, lifespan="off")
