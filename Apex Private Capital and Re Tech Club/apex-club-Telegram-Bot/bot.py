"""APEX ASSET SUITE — ADIPEC Concierge Bot (Ясмина)
=====================================================
Гибридная система: Telegram Bot + Telegram WebApp (TWA)

Архитектура:
  /start → Приветствие бота «Ясмина» (KYC-комплаенс)
    ├── KYC-скрининг:
    │     1. Сбор ФИО + сфера деятельности
    │     2. Финансовый фильтр ($100,000 ликвидный капитал)
    │     3. Мультивыбор инвест-предпочтений
    │     4. Финализация → комплаенс-проверка
    │
    ├── Контур А (Гостевой) — до прохождения KYC
    ├── Контур Б (Резидент)  — после KYC
    └── Контур Г (VIP КМГ)   — авторизация по @kmg.kz

  WebApp → Открывает TWA (Расписание / Нетворкинг / Консьерж / Оффер)
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import sys
from datetime import datetime
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

# Google Sheets (legacy — в будущем заменяется на Backend API)
import gspread
from google.oauth2.service_account import Credentials

# dotenv для загрузки .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv опционален

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1.  КОНФИГУРАЦИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не задан. Создайте .env файл или задайте переменную окружения.")
    sys.exit(1)

WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://your-domain.com")
SUPPORT_USERNAME: str = os.getenv("SUPPORT_USERNAME", "@appex_support")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, os.getenv("CREDENTIALS_FILE", "credentials.json"))
SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "1szL5sNAQMN0c90kb9j8Z8Qiw3mZ6Kpmj3EaYsErO8Lw")

SHEET_RESIDENTS = "Резиденты"
SHEET_WAITLIST  = "waitlist"
SHEET_APPROVED  = "Approved"
SHEET_LEADS     = "Лиды & События"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Минимальный порог капитала для входа в клуб (USD)
MIN_CAPITAL_THRESHOLD = 100_000

# Стоп-слова для автоматического скрининга
STOP_WORDS = {
    "студент", "student", "безработн", "без работы", "не работаю",
    "школьник", "пенсионер", "мошенник", "спам", "spam",
    "без денег", "нет денег", "ищу спонсора", "ищу инвестора",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2.  ТЕКСТЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEXTS: dict[str, str] = {
    # ── Приветствие Ясмины ──
    "welcome": (
        "🏛 <b>Добро пожаловать в APEX ASSET SUITE.</b>\n\n"
        "Я — <b>Ясмина</b>, ваш цифровой консьерж и ассистент по инвестициям.\n\n"
        "Для доступа к инвестиционному маркетплейсу и сервисам ADIPEC Concierge, "
        "пожалуйста, пройдите верификацию.\n\n"
        "<i>Нажмите кнопку ниже для начала.</i>"
    ),

    # ── KYC Ясмины (пошагово) ──
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
        f"По вопросам: {SUPPORT_USERNAME}"
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
        f"По срочным вопросам: {SUPPORT_USERNAME}"
    ),

    # ── Авторизация (legacy) ──
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
        f"Для связи с менеджером: {SUPPORT_USERNAME}\n\n"
        "Мы доступны с 10:00 до 20:00 (UTC+4, Abu Dhabi)."
    ),

    # ── Общие ──
    "not_understood": "⚠️ Действие не распознано. Выберите один из предложенных вариантов.",
    "cancelled": "❌ Действие отменено. Возвращаемся в главное меню…",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3.  ЛОГИРОВАНИЕ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4.  GOOGLE SHEETS — ASYNC WRAPPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_gspread_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


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
        ws = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        ws.append_row(row)

    try:
        await asyncio.to_thread(_append)
        logger.info("Row saved to sheet '%s': %s", sheet_name, row[:3])
    except Exception:
        logger.exception("sheets_append error for %s", sheet_name)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5.  FSM СОСТОЯНИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KycFSM(StatesGroup):
    """KYC-скрининг «Ясмина»"""
    fio_and_business = State()  # Шаг 1: ФИО + сфера
    capital_check    = State()  # Шаг 2: Финансовый ценз
    preferences      = State()  # Шаг 3: Инвест-предпочтения


class AuthFSM(StatesGroup):
    """Legacy-авторизация по контакту"""
    waiting_contact = State()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.  КЛАВИАТУРЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _inline(*rows: tuple[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=d)] for t, d in rows
        ]
    )


def _welcome_kb() -> InlineKeyboardMarkup:
    """Главное приветственное меню Ясмины"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Подать заявку на вступление", callback_data="kyc_start")],
        [InlineKeyboardButton(text="🔐 У меня уже есть членство", callback_data="auth_start")],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_support")],
    ])


def _capital_kb() -> InlineKeyboardMarkup:
    """Клавиатура финансового ценза"""
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
    """Мультивыбор инвест-предпочтений"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏎 Спорткары Porsche / Maserati", callback_data="pref_cars")],
        [InlineKeyboardButton(text="🏠 Недвижимость ОАЭ (офплан)", callback_data="pref_realestate")],
        [InlineKeyboardButton(text="🔄 P2P выход (вторичный рынок)", callback_data="pref_p2p")],
        [InlineKeyboardButton(text="📊 Все направления", callback_data="pref_all")],
    ])


def _main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню после авторизации / KYC"""
    buttons = [
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=WEBAPP_URL),
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
    """Меню после завершения KYC"""
    buttons = [
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_support")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7.  РОУТЕР И ОБРАБОТЧИКИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = Router(name="main")


# ──── /start ────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TEXTS["welcome"], reply_markup=_welcome_kb())
    logger.info("User %s started the bot.", message.from_user.id)


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
    """Прямой доступ к WebApp через команду"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )],
    ])
    await message.answer("Нажмите кнопку ниже для запуска приложения:", reply_markup=kb)


# ──── KYC «Ясмина» ────

@router.callback_query(F.data == "kyc_start")
async def kyc_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Шаг 1: запрос ФИО и сферы деятельности"""
    await state.clear()
    await state.set_state(KycFSM.fio_and_business)
    await callback.message.answer(TEXTS["kyc_fio"])
    await callback.answer()


@router.message(KycFSM.fio_and_business, F.text)
async def kyc_fio_received(message: Message, state: FSMContext) -> None:
    """Получили ФИО + сферу → переходим к финансовому цензу"""
    await state.update_data(fio_and_business=message.text)
    await state.set_state(KycFSM.capital_check)
    await message.answer(TEXTS["kyc_capital"], reply_markup=_capital_kb())


@router.callback_query(KycFSM.capital_check, F.data == "capital_yes")
async def kyc_capital_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    """Капитал подтверждён → инвест-предпочтения"""
    await state.update_data(capital_confirmed=True)
    await state.set_state(KycFSM.preferences)
    await callback.message.edit_text(
        f"✅ Финансовый ценз подтверждён (> ${MIN_CAPITAL_THRESHOLD:,})"
    )
    await callback.message.answer(TEXTS["kyc_preferences"], reply_markup=_preferences_kb())
    await callback.answer()


@router.callback_query(KycFSM.capital_check, F.data == "capital_no")
async def kyc_capital_rejected(callback: CallbackQuery, state: FSMContext) -> None:
    """Жёсткий барьер: капитал < $100,000 — немедленное завершение"""
    await state.clear()
    await callback.message.edit_text(TEXTS["kyc_capital_reject"])
    await callback.answer()
    logger.info("KYC REJECTED (capital): user=%s", callback.from_user.id)


@router.callback_query(KycFSM.preferences, F.data.startswith("pref_"))
async def kyc_preferences_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Шаг 3: инвест-предпочтения выбраны → финализация"""
    pref_map = {
        "pref_cars": "Спорткары (Porsche/Maserati)",
        "pref_realestate": "Недвижимость ОАЭ",
        "pref_p2p": "P2P выход (вторичный рынок)",
        "pref_all": "Все направления",
    }
    preference = pref_map.get(callback.data, callback.data)
    await state.update_data(preference=preference)
    data = await state.get_data()

    # Объединяем все ответы для скрининга
    combined = " ".join([
        data.get("fio_and_business", ""),
        preference,
    ]).lower()

    has_stop_word = any(word in combined for word in STOP_WORDS)

    # Формируем запись
    row_data = [
        str(callback.from_user.id),
        callback.from_user.username or "",
        data.get("fio_and_business", ""),
        f"Капитал > ${MIN_CAPITAL_THRESHOLD:,}",
        preference,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]

    if has_stop_word:
        await sheets_append(SHEET_WAITLIST, row_data + ["⚠️ Стоп-слово (автоскрининг)"])
        await state.clear()
        await callback.message.edit_text(TEXTS["kyc_flagged"])
        logger.info("KYC FLAGGED: user=%s", callback.from_user.id)
    else:
        await sheets_append(SHEET_APPROVED, row_data + ["✅ Автоскрининг пройден"])
        await state.clear()
        await callback.message.edit_text(
            f"🎯 Выбрано направление: <b>{preference}</b>"
        )
        await callback.message.answer(TEXTS["kyc_finalize"], reply_markup=_post_kyc_kb())
        logger.info(
            "KYC PASSED: user=%s fio=%s pref=%s",
            callback.from_user.id, data.get("fio_and_business"), preference,
        )

    await callback.answer()


# ──── Legacy-авторизация (Контакт) ────

@router.callback_query(F.data == "auth_start")
async def auth_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AuthFSM.waiting_contact)
    await callback.message.answer(TEXTS["auth_check"], reply_markup=_auth_kb())
    await callback.answer()


@router.message(AuthFSM.waiting_contact, F.contact)
async def auth_contact_received(message: Message, state: FSMContext) -> None:
    """Получаем контакт, ищем в Google Sheets."""
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
        logger.info("Auth SUCCESS: user=%s", message.from_user.id)
    else:
        await state.clear()
        await message.answer(TEXTS["auth_fail"], reply_markup=_welcome_kb())
        logger.info("Auth FAIL: user=%s phone=%s", message.from_user.id, phone)


@router.message(AuthFSM.waiting_contact, ~F.contact)
async def auth_text_instead_of_contact(message: Message) -> None:
    await message.answer(TEXTS["contact_required"], reply_markup=_auth_kb())


# ──── Служба поддержки ────

@router.callback_query(F.data == "contact_support")
async def contact_support_callback(callback: CallbackQuery) -> None:
    kb = _inline(("⬅️ В начало", "go_start"))
    await callback.message.answer(TEXTS["support"], reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "go_start")
async def go_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(TEXTS["welcome"], reply_markup=_welcome_kb())
    await callback.answer()


# ──── Fallback ────

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
# 8.  ТОЧКА ВХОДА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)
    logger.info("🚀 APEX ASSET SUITE Bot (Ясмина) starting polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())