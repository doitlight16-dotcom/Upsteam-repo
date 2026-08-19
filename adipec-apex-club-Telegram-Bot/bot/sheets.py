"""Google Sheets async wrapper — APEX ASSET SUITE"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "1szL5sNAQMN0c90kb9j8Z8Qiw3mZ6Kpmj3EaYsErO8Lw")
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", os.getenv("CREDENTIALS_FILE", "credentials.json"))

SHEET_RESIDENTS = "Резиденты"
SHEET_WAITLIST  = "waitlist"
SHEET_APPROVED  = "Approved"
SHEET_LEADS     = "Лиды & События"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _get_gspread_client() -> gspread.Client | None:
    try:
        json_env = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or os.getenv("CREDENTIALS_JSON")
        if json_env:
            try:
                info = json.loads(json_env)
                # Фикс для Vercel: восстанавливаем переносы строк в приватном ключе
                if "private_key" in info:
                    info["private_key"] = info["private_key"].replace("\\n", "\n")
                
                creds = Credentials.from_service_account_info(info, scopes=SCOPES)
                return gspread.authorize(creds)
            except Exception as e:
                logger.error(f"❌ Ошибка авторизации Google Sheets из JSON: {e}")

        if os.path.exists(CREDENTIALS_FILE):
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            return gspread.authorize(creds)

        logger.error("❌ Учетные данные Google Sheets не найдены (ни JSON, ни файл).")
        return None
    except Exception as e:
        logger.error(f"❌ Общая ошибка авторизации Google Sheets: {e}")
        return None


def _normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits


async def sheets_lookup_phone(phone: str) -> dict | None:
    """Ищет резидента по номеру телефона. Возвращает dict или None."""
    normalized = _normalize_phone(phone)

    def _lookup():
        client = _get_gspread_client()
        if not client:
            return None
        ws = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_RESIDENTS)
        records = ws.get_all_records()
        for row in records:
            raw = str(row.get("Телефон", ""))
            if _normalize_phone(raw) == normalized:
                return row
        return None

    try:
        return await asyncio.to_thread(_lookup)
    except Exception:
        logger.exception("sheets_lookup_phone error for %s", phone)
        return None


async def sheets_append(sheet_name: str, row: list) -> None:
    def _append():
        client = _get_gspread_client()
        if not client:
            return
        ws = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        ws.append_row(row)

    try:
        await asyncio.to_thread(_append)
        logger.info("Row saved to sheet '%s': %s", sheet_name, row[:3])
    except Exception:
        logger.exception("sheets_append error for %s", sheet_name)
