"""Клавиатуры — APEX ASSET SUITE / ADIPEC Concierge Bot"""

import os

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://appex-adipec-concierge.vercel.app")
MIN_CAPITAL_THRESHOLD = 100_000


def _inline(*rows: tuple[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=d)] for t, d in rows
        ]
    )


def welcome_kb() -> InlineKeyboardMarkup:
    """Главное приветственное меню Ясмины"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Подать заявку на вступление", callback_data="kyc_start")],
        [InlineKeyboardButton(text="🔐 У меня уже есть членство", callback_data="auth_start")],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_support")],
    ])


def capital_kb() -> InlineKeyboardMarkup:
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


def preferences_kb() -> InlineKeyboardMarkup:
    """Мультивыбор инвест-предпочтений"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏎 Спорткары Porsche / Maserati", callback_data="pref_cars")],
        [InlineKeyboardButton(text="🏠 Недвижимость ОАЭ (офплан)", callback_data="pref_realestate")],
        [InlineKeyboardButton(text="🔄 P2P выход (вторичный рынок)", callback_data="pref_p2p")],
        [InlineKeyboardButton(text="📊 Все направления", callback_data="pref_all")],
    ])


def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню после авторизации / KYC"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )],
        [InlineKeyboardButton(text="📞 Служба заботы", callback_data="contact_support")],
    ])


def auth_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔐 Подтвердить членство", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def post_kyc_kb() -> InlineKeyboardMarkup:
    """Меню после завершения KYC"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🌐 Открыть ADIPEC Concierge",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_support")],
    ])


def back_to_start_kb() -> InlineKeyboardMarkup:
    return _inline(("⬅️ В начало", "go_start"))
