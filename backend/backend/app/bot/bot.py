"""APEX ASSET SUITE — ADIPEC Concierge Bot.

Hybrid system: Telegram Bot + Telegram WebApp (TWA).
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
import os
import re
import sys
from typing import Any

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Contact,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1.  КОНФИГУРАЦИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_bot_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN", "")

def get_webapp_url() -> str:
    return os.getenv("WEBAPP_URL", "https://appex-adipec-concierge.vercel.app")

def get_support_username() -> str:
    return os.getenv("SUPPORT_USERNAME", "@appex_support")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
if not os.path.isabs(CREDENTIALS_FILE):
    CREDENTIALS_FILE = os.path.join(BASE_DIR, CREDENTIALS_FILE)

SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "1szL5sNAQMN0c90kb9j8Z8Qiw3mZ6Kpmj3EaYsErO8Lw")

SHEET_RESIDENTS = "Резиденты"
SHEET_WAITLIST  = "waitlist"
SHEET_APPROVED  = "Approved"
SHEET_LEADS     = "Лиды & События"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MIN_CAPITAL_THRESHOLD = 100_000

STOP_WORDS = {
    "студент", "student", "безработн", "без работы", "не работаю",
    "школьник", "пенсионер", "мошенник", "спам", "spam",
    "без денег", "нет денег", "ищу спонсора", "ищу инвестора",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2.  ТЕКСТЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEXTS: dict[str, str] = {
    # ── Приветствие ──
    "welcome": (
        "🏛 <b>Добро пожаловать в APEX ASSET SUITE.</b>\n\n"
        "Я — ваш <b>цифровой консьерж</b> и ассистент по инвестициям.\n\n"
        "Для доступа к инвестиционному маркетплейсу и сервисам ADIPEC Concierge, "
        "пожалуйста, пройдите верификацию.\n\n"
        "<i>Нажмите кнопку ниже для начала.</i>"
    ),

    # ── KYC (пошагово) ──
    "kyc_fio": (
        "📋 <b>Шаг 1 из 4 — Идентификация</b>\n\n"
        "Пожалуйста, укажите ваше <b>ФИО</b> и <b>сферу деятельности</b>.\n\n"
        "<i>Пример: Иванов Иван Петрович, нефтегазовая промышленность</i>"
    ),
    "kyc_capital": (
        "💎 <b>Шаг 2 из 4 — Финансовый ценз</b>\n\n"
        "Членство в клубе доступно инвесторам с минимальным порогом "
        f"ликвидного капитала от <b>${MIN_CAPITAL_THRESHOLD:,}</b>.\n\n"
        "Подтверждаете ли вы соответствие данному цензу?"
    ),
    "kyc_capital_reject": (
        "🚫 <b>Благодарим за интерес.</b>\n\n"
        "На данном этапе пул закрыт для розничных инвесторов.\n\n"
        f"По вопросам: {get_support_username()}"
    ),
    "kyc_preferences": (
        "🎯 <b>Шаг 3 из 4 — Инвестиционные предпочтения</b>\n\n"
        "Выберите интересующие вас направления:"
    ),
    "kyc_finalize": (
        "✅ <b>Шаг 4 из 4 — Заявка принята!</b>\n\n"
        "Ваша заявка направлена на комплаенс-проверку управляющему клуба.\n"
        "Ожидайте уведомления в течение 48 часов.\n\n"
        "А пока вы можете ознакомиться с нашим приложением ADIPEC Concierge:"
    ),
    "kyc_flagged": (
        "📋 <b>Заявка принята на рассмотрение.</b>\n\n"
        "Ваша анкета будет изучена нашей командой. "
        "Мы свяжемся с вами в течение 5 рабочих дней.\n\n"
        f"По срочным вопросам: {get_support_username()}"
    ),

    # ── Авторизация ──
    "auth_check": (
        "🔐 <b>Верификация членства</b>\n\n"
        "Для проверки вашего статуса в реестре резидентов, "
        "нажмите кнопку ниже.\n\n"
        "<i>Ваш номер будет сверён с базой участников клуба.</i>"
    ),
    "auth_success": (
        "✅ <b>Авторизация успешна.</b>\n\n"
        "Рады видеть вас в клубе, <b>{name}</b>!\n"
        "Ваш статус: <b>{status}</b>.\n\n"
        "Выберите действие:"
    ),
    "auth_fail": (
        "🚫 Указанный номер <b>отсутствует</b> в реестре.\n\n"
        "Вы можете подать заявку на вступление или связаться с нами."
    ),
    "contact_required": (
        "⚠️ Для верификации необходимо нажать кнопку "
        "<b>«🔐 Подтвердить членство»</b> ниже.\n\n"
        "Ручной ввод номера не принимается в целях безопасности."
    ),

    # ── Главное меню ──
    "main_menu": (
        "🏛 <b>APEX ASSET SUITE</b>\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        "Выберите раздел:"
    ),

    # ── Служба поддержки ──
    "support": (
        f"📞 <b>Служба заботы о клиентах</b>\n\n"
        f"Для связи с менеджером: {get_support_username()}\n\n"
        "Мы доступны с 10:00 до 20:00 (UTC+4, Abu Dhabi)."
    ),

    # ── Общие ──
    "not_understood": "⚠️ Действие не распознано. Выберите один из предложенных вариантов.",
    "cancelled": "❌ Действие отменено. Возвращаемся в главное меню…",
}


import json

def _get_gspread_client() -> gspread.Client | None:
    try:
        json_env = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or os.getenv("CREDENTIALS_JSON")
        if json_env:
            raw = json_env.strip()
            # If wrapped in quotes, unwrap
            if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]
            try:
                info = json.loads(raw)
            except Exception:
                try:
                    # Attempt unescaping if string contains literal \n and \"
                    raw_unescaped = raw.encode("utf-8").decode("unicode_escape")
                    info = json.loads(raw_unescaped)
                except Exception as e:
                    logger.warning(f"Google Sheets auth from JSON env failed: {e}")
                    info = None

            if info and isinstance(info, dict):
                creds = Credentials.from_service_account_info(info, scopes=SCOPES)
                return gspread.authorize(creds)

        if os.path.exists(CREDENTIALS_FILE):
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            return gspread.authorize(creds)

        logger.warning(f"Google Sheets credentials not found at {CREDENTIALS_FILE} and no GOOGLE_SERVICE_ACCOUNT_JSON env var.")
        return None
    except Exception as e:
        logger.warning(f"Google Sheets auth failed: {e}")
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4.  FSM СОСТОЯНИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KycFSM(StatesGroup):
    """KYC-скрининг"""
    fio_and_business = State()
    capital_check    = State()
    preferences      = State()


class AuthFSM(StatesGroup):
    """Авторизация по контакту"""
    waiting_contact = State()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5.  КЛАВИАТУРЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _inline(*rows: tuple[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=d)] for t, d in rows
        ]
    )


def _welcome_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Подать заявку на вступление", callback_data="kyc_start")],
        [InlineKeyboardButton(text="🔐 У меня уже есть членство", callback_data="auth_start")],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_support")],
    ])


def _capital_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"✅ Да, мой капитал > ${MIN_CAPITAL_THRESHOLD:,}",
            callback_data="capital_yes",
        )],
        [InlineKeyboardButton(
            text="❌ Нет, сумма меньше",
            callback_data="capital_no",
        )],
    ])


def _preferences_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏎 Спорткары Porsche / Maserati", callback_data="pref_cars")],
        [InlineKeyboardButton(text="🏠 Недвижимость ОАЭ (офплан)", callback_data="pref_realestate")],
        [InlineKeyboardButton(text="🔄 P2P выход (вторичный рынок)", callback_data="pref_p2p")],
        [InlineKeyboardButton(text="📊 Все направления", callback_data="pref_all")],
    ])


def _main_menu_kb() -> InlineKeyboardMarkup:
    webapp_url = get_webapp_url()
    buttons = [
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=webapp_url),
        )],
        [InlineKeyboardButton(text="📞 Служба заботы", callback_data="contact_support")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _auth_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔐 Подтвердить членство", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _post_kyc_kb() -> InlineKeyboardMarkup:
    webapp_url = get_webapp_url()
    buttons = [
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=webapp_url),
        )],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_support")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.  РОУТЕР И ОБРАБОТЧИКИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = Router(name="bot_main")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TEXTS["welcome"], reply_markup=_welcome_kb())
    logger.info("User %s started the bot.", message.from_user.id if message.from_user else "unknown")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TEXTS["cancelled"], reply_markup=ReplyKeyboardRemove())
    await message.answer(TEXTS["welcome"], reply_markup=_welcome_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer(TEXTS["main_menu"], reply_markup=_main_menu_kb())


@router.message(Command("webapp"))
async def cmd_webapp(message: Message) -> None:
    webapp_url = get_webapp_url()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=webapp_url),
        )],
    ])
    await message.answer("Нажмите кнопку ниже для запуска приложения:", reply_markup=kb)


# ──── KYC ────

@router.callback_query(F.data == "kyc_start")
async def kyc_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(KycFSM.fio_and_business)
    if callback.message:
        await callback.message.answer(TEXTS["kyc_fio"])
    await callback.answer()


@router.message(KycFSM.fio_and_business, F.text)
async def kyc_fio_received(message: Message, state: FSMContext) -> None:
    await state.update_data(fio_and_business=message.text)
    await state.set_state(KycFSM.capital_check)
    await message.answer(TEXTS["kyc_capital"], reply_markup=_capital_kb())


@router.callback_query(KycFSM.capital_check, F.data == "capital_yes")
async def kyc_capital_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(capital_confirmed=True)
    await state.set_state(KycFSM.preferences)
    if callback.message and isinstance(callback.message, types.Message):
        await callback.message.edit_text(
            f"✅ Финансовый ценз подтверждён (> ${MIN_CAPITAL_THRESHOLD:,})"
        )
        await callback.message.answer(TEXTS["kyc_preferences"], reply_markup=_preferences_kb())
    await callback.answer()


@router.callback_query(KycFSM.capital_check, F.data == "capital_no")
async def kyc_capital_rejected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message and isinstance(callback.message, types.Message):
        await callback.message.edit_text(TEXTS["kyc_capital_reject"])
    await callback.answer()
    logger.info("KYC REJECTED (capital): user=%s", callback.from_user.id if callback.from_user else "unknown")


@router.callback_query(KycFSM.preferences, F.data.startswith("pref_"))
async def kyc_preferences_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    pref_map = {
        "pref_cars": "Спорткары (Porsche/Maserati)",
        "pref_realestate": "Недвижимость ОАЭ",
        "pref_p2p": "P2P выход (вторичный рынок)",
        "pref_all": "Все направления",
    }
    pref_key = callback.data or ""
    preference = pref_map.get(pref_key, pref_key)
    await state.update_data(preference=preference)
    data = await state.get_data()

    combined = " ".join([
        data.get("fio_and_business", ""),
        preference,
    ]).lower()

    has_stop_word = any(word in combined for word in STOP_WORDS)

    user_id = str(callback.from_user.id) if callback.from_user else ""
    username = callback.from_user.username or "" if callback.from_user else ""

    row_data = [
        user_id,
        username,
        data.get("fio_and_business", ""),
        f"Капитал > ${MIN_CAPITAL_THRESHOLD:,}",
        preference,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]

    if callback.message and isinstance(callback.message, types.Message):
        if has_stop_word:
            await sheets_append(SHEET_WAITLIST, row_data + ["⚠️ Стоп-слово (автоскрининг)"])
            await state.clear()
            await callback.message.edit_text(TEXTS["kyc_flagged"])
            logger.info("KYC FLAGGED: user=%s", user_id)
        else:
            await sheets_append(SHEET_APPROVED, row_data + ["✅ Автоскрининг пройден"])
            await state.clear()
            await callback.message.edit_text(
                f"🎯 Выбрано направление: <b>{preference}</b>"
            )
            await callback.message.answer(TEXTS["kyc_finalize"], reply_markup=_post_kyc_kb())
            logger.info("KYC PASSED: user=%s fio=%s pref=%s", user_id, data.get("fio_and_business"), preference)

    await callback.answer()


# ──── Авторизация (Контакт) ────

@router.callback_query(F.data == "auth_start")
async def auth_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AuthFSM.waiting_contact)
    if callback.message:
        await callback.message.answer(TEXTS["auth_check"], reply_markup=_auth_kb())
    await callback.answer()


@router.message(AuthFSM.waiting_contact, F.contact)
async def auth_contact_received(message: Message, state: FSMContext) -> None:
    if not message.contact:
        return
    phone = message.contact.phone_number
    await message.answer("🔍 Проверяю данные…", reply_markup=ReplyKeyboardRemove())

    resident = await sheets_lookup_phone(phone)

    if resident:
        await state.clear()
        await state.update_data(resident=resident)
        await message.answer(
            TEXTS["auth_success"].format(
                name=resident.get("Имя", resident.get("name", "Резидент")),
                status=resident.get("Статус", resident.get("status", "Резидент")),
            ),
            reply_markup=_main_menu_kb(),
        )
        logger.info("Auth SUCCESS: user=%s", message.from_user.id if message.from_user else "")
    else:
        await state.clear()
        await message.answer(TEXTS["auth_fail"], reply_markup=_welcome_kb())
        logger.info("Auth FAIL: user=%s phone=%s", message.from_user.id if message.from_user else "", phone)


@router.message(AuthFSM.waiting_contact, ~F.contact)
async def auth_text_instead_of_contact(message: Message) -> None:
    await message.answer(TEXTS["contact_required"], reply_markup=_auth_kb())


# ──── Служба поддержки ────

@router.callback_query(F.data == "contact_support")
async def contact_support_callback(callback: CallbackQuery) -> None:
    kb = _inline(("⬅️ В начало", "go_start"))
    if callback.message:
        await callback.message.answer(TEXTS["support"], reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "go_start")
async def go_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.answer(TEXTS["welcome"], reply_markup=_welcome_kb())
    await callback.answer()


@router.callback_query()
async def unmatched_callback(callback: CallbackQuery) -> None:
    await callback.answer(TEXTS["not_understood"], show_alert=True)


@router.message()
async def general_fallback(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current and current.startswith("AuthFSM"):
        await message.answer(TEXTS["contact_required"], reply_markup=_auth_kb())
    elif current and current.startswith("KycFSM"):
        await message.answer(TEXTS["not_understood"])
    else:
        await message.answer(
            "Нажмите /start для начала работы.",
            reply_markup=ReplyKeyboardRemove(),
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7.  ТОЧКА ЗАПУСКА В FASTAPI LIFESPAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start_bot() -> None:
    token = get_bot_token()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN / BOT_TOKEN is empty. Telegram bot will not start.")
        return

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("🚀 APEX ASSET SUITE Telegram Bot starting polling...")
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("Telegram Bot polling stopped.")
    except Exception as e:
        logger.error(f"Telegram Bot encountered an error: {e}", exc_info=True)
    finally:
        await bot.session.close()
