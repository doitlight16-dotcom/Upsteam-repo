"""FSM состояния — APEX ASSET SUITE / ADIPEC Concierge Bot"""

from aiogram.fsm.state import State, StatesGroup


class KycFSM(StatesGroup):
    """KYC-скрининг «Ясмина»"""
    fio_and_business = State()  # Шаг 1: ФИО + сфера
    capital_check    = State()  # Шаг 2: Финансовый ценз
    preferences      = State()  # Шаг 3: Инвест-предпочтения


class AuthFSM(StatesGroup):
    """Legacy-авторизация по контакту"""
    waiting_contact = State()
