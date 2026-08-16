from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import os
import jwt
from datetime import datetime, timedelta

from app.infrastructure.telegram.auth import verify_telegram_init_data, parse_user_from_init_data

router = APIRouter(prefix="/auth", tags=["Auth"])

# В продакшене использовать переменные окружения
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_jwt_key_for_adipec")
BOT_TOKEN = os.getenv("BOT_TOKEN", "mock_bot_token")

class AuthRequest(BaseModel):
    initData: str

class AuthResponse(BaseModel):
    token: str
    user: dict

@router.post("/telegram")
async def telegram_auth(req: AuthRequest):
    if not req.initData:
        raise HTTPException(status_code=400, detail="Missing initData")
    
    # В дев-режиме можно пропустить жесткую проверку, если токен не задан
    if BOT_TOKEN != "mock_bot_token":
        is_valid = verify_telegram_init_data(req.initData, BOT_TOKEN)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram signature")

    user_data = parse_user_from_init_data(req.initData)
    if not user_data:
        raise HTTPException(status_code=400, detail="User data missing in initData")
        
    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID missing")

    # Создание JWT токена (срок действия 24 часа)
    payload = {
        "sub": str(telegram_id),
        "username": user_data.get("username"),
        "role": "GUEST", # По-умолчанию, далее - из БД
        "tenant_id": "Appex_Main",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return AuthResponse(token=token, user=user_data)
