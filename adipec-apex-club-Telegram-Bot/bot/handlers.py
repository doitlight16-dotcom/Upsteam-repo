"""Обработчики сообщений и колбэков — APEX ASSET SUITE / ADIPEC Concierge Bot"""

from __future__ import annotations

import logging
import os
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from .keyboards import (
    auth_kb,
    back_to_start_kb,
    capital_kb,
    main_menu_kb,
    post_kyc_kb,
    preferences_kb,
    welcome_kb,
)
from .sheets import (
    SHEET_APPROVED,
    SHEET_WAITLIST,
    sheets_append,
    sheets_lookup_phone,
)
from .states import AuthFSM, KycFSM

logger = logging.getLogger(__name__)

SUPPORT_USERNAME: str = os.getenv("SUPPORT_USERNAME", "@appex_support")
MIN_CAPITAL_THRESHOLD = 100_000

# Стоп-слова для автоматического скрининга
STOP_WORDS = {
    "студент", "student", "безработн", "без работы", "не работаю",
    "школьник", "пенсионер", "мошенник", "спам", "spam",
    "без денег", "нет денег", "ищу спонсора", "ищу инвестора",
}

TEXTS: dict[str, str] = {
    # ── Приветствие Ясмины ──
    "welcome": (
        "🏛 <b>Добро пожаловать в APEX ASSET SUITE.</b>\n\n"
        "Я — ваш <b>цифровой консьерж</b> и ассистент по инвестициям.\n\n"
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


def build_router() -> Router:
    """Создаёт и возвращает настроенный Router со всеми обработчиками."""
    router = Router(name="main")

    # ──── /start ────

    @router.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(TEXTS["welcome"], reply_markup=welcome_kb())
        logger.info("User %s started the bot.", message.from_user.id)

    @router.message(Command("cancel"))
    async def cmd_cancel(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(TEXTS["cancelled"], reply_markup=ReplyKeyboardRemove())
        await message.answer(TEXTS["welcome"], reply_markup=welcome_kb())

    @router.message(Command("menu"))
    async def cmd_menu(message: Message) -> None:
        await message.answer(TEXTS["main_menu"], reply_markup=main_menu_kb())

    @router.message(Command("webapp"))
    async def cmd_webapp(message: Message) -> None:
        """Прямой доступ к WebApp через команду"""
        from aiogram.types import InlineKeyboardButton, WebAppInfo
        import os
        webapp_url = os.getenv("WEBAPP_URL", "https://appex-adipec-concierge.vercel.app")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🌐 Открыть ADIPEC Concierge",
                web_app=WebAppInfo(url=webapp_url),
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
        await message.answer(TEXTS["kyc_capital"], reply_markup=capital_kb())

    @router.callback_query(KycFSM.capital_check, F.data == "capital_yes")
    async def kyc_capital_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
        """Капитал подтверждён → инвест-предпочтения"""
        await state.update_data(capital_confirmed=True)
        await state.set_state(KycFSM.preferences)
        await callback.message.edit_text(
            f"✅ Финансовый ценз подтверждён (> ${MIN_CAPITAL_THRESHOLD:,})"
        )
        await callback.message.answer(TEXTS["kyc_preferences"], reply_markup=preferences_kb())
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

        combined = " ".join([
            data.get("fio_and_business", ""),
            preference,
        ]).lower()

        has_stop_word = any(word in combined for word in STOP_WORDS)

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
            await callback.message.answer(TEXTS["kyc_finalize"], reply_markup=post_kyc_kb())
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
        await callback.message.answer(TEXTS["auth_check"], reply_markup=auth_kb())
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
                reply_markup=main_menu_kb(),
            )
            logger.info("Auth SUCCESS: user=%s", message.from_user.id)
        else:
            await state.clear()
            await message.answer(TEXTS["auth_fail"], reply_markup=welcome_kb())
            logger.info("Auth FAIL: user=%s phone=%s", message.from_user.id, phone)

    @router.message(AuthFSM.waiting_contact, ~F.contact)
    async def auth_text_instead_of_contact(message: Message) -> None:
        await message.answer(TEXTS["contact_required"], reply_markup=auth_kb())

    # ──── Служба поддержки ────

    @router.callback_query(F.data == "contact_support")
    async def contact_support_callback(callback: CallbackQuery) -> None:
        await callback.message.answer(TEXTS["support"], reply_markup=back_to_start_kb())
        await callback.answer()

    @router.callback_query(F.data == "go_start")
    async def go_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.message.answer(TEXTS["welcome"], reply_markup=welcome_kb())
        await callback.answer()

    # ──── Fallback ────

    @router.callback_query()
    async def unmatched_callback(callback: CallbackQuery) -> None:
        await callback.answer(TEXTS["not_understood"], show_alert=True)

    @router.message()
    async def general_fallback(message: Message, state: FSMContext) -> None:
        current = await state.get_state()
        if current and current.startswith("AuthFSM"):
            await message.answer(TEXTS["contact_required"], reply_markup=auth_kb())
        elif current and current.startswith("KycFSM"):
            await message.answer(TEXTS["not_understood"])
        else:
            await message.answer(
                "Нажмите /start для начала работы.",
                reply_markup=ReplyKeyboardRemove(),
            )

    return router
