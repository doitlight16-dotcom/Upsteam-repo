"""APEX ASSET SUITE — AI Concierge Context Builder
====================================================
Assembles structured domain data into an LLM system prompt.

In production, these data sources would be queried from databases.
Currently uses demo data mirrored from the frontend App.jsx.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOMAIN DATA (demo — mirrors App.jsx constants)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELEGATE = {
    "name": "Асхат Ержанов",
    "role": "Директор департамента международных партнёрств",
    "org": "АО «НК «КазМунайГаз»",
    "badge": "KMG-DLG-0417",
}

SCHEDULE = [
    {"time": "09:30", "title": "Открытие павильона КМГ", "place": "Холл 7, стенд A12", "tag": "Официально"},
    {"time": "11:15", "title": "Панель: энергопереход в Центральной Азии", "place": "Конференц-зал 3", "tag": "Сессия"},
    {"time": "14:00", "title": "Встреча с ADNOC", "place": "VIP-лаундж 2", "tag": "Переговоры"},
    {"time": "18:30", "title": "Приём для делегатов КМГ", "place": "Emirates Palace, зал Al Majlis", "tag": "Приём"},
]

FLEET = [
    {
        "id": "car1",
        "model": "Mercedes-Benz S-Class",
        "plate": "AUH 4471",
        "driver": "Юсуф Аль-Кетби",
        "lang": "EN / RU",
        "phone": "+971 50 118 22 41",
        "eta": "4 мин",
        "status": "На парковке P3",
    },
    {
        "id": "car2",
        "model": "Maybach S 680",
        "plate": "AUH 9902",
        "driver": "Дмитрий Коваль",
        "lang": "RU / EN",
        "phone": "+971 55 700 91 03",
        "eta": "7 мин",
        "status": "В пути к Холлу 7",
    },
    {
        "id": "car3",
        "model": "Mercedes V-Class (минивэн)",
        "plate": "AUH 5518",
        "driver": "Омар Хассан",
        "lang": "EN / AR",
        "phone": "+971 52 340 65 19",
        "eta": "2 мин",
        "status": "Ожидает у входа B",
    },
]

PARTNERS = [
    {
        "id": "p1",
        "company": "ADNOC",
        "person": "Sultan Al Mazrouei",
        "title": "SVP, International Growth",
        "country": "ОАЭ",
        "lounge": "VIP-лаундж 2",
        "minutes_left": 47,
        "brief": "Интерес к совместным нефтесервисным СП в бассейне Каспия. "
                 "Ранее обсуждали своп-соглашения по СПГ на форуме в Дубае.",
    },
    {
        "id": "p2",
        "company": "Saudi Aramco",
        "person": "Faisal Al-Qahtani",
        "title": "Director, Downstream Ventures",
        "country": "Саудовская Аравия",
        "lounge": "VIP-лаундж 1",
        "minutes_left": 132,
        "brief": "Рассматривают партнёрство по нефтехимии. На стороне КМГ — "
                 "интерес к обмену технологиями глубокой переработки.",
    },
    {
        "id": "p3",
        "company": "TotalEnergies",
        "person": "Claire Dubosc",
        "title": "VP, Central Asia & Caspian",
        "country": "Франция",
        "lounge": "VIP-лаундж 3",
        "minutes_left": 268,
        "brief": "Продление действующего СРП обсуждалось в Q2. "
                 "Готовы к разговору о декарбонизации добычи.",
    },
]

LOTS = [
    {
        "id": "l1",
        "kind": "Недвижимость",
        "title": "Коммерческий блок, Al Reem Island",
        "detail": "890 м² рядом с ADNEC, класс A",
        "roi": "8.4%",
    },
    {
        "id": "l2",
        "kind": "Недвижимость",
        "title": "Офисные лоты, Capital Centre",
        "detail": "1 200 м², сдача 2027",
        "roi": "9.1%",
    },
    {
        "id": "l3",
        "kind": "Авто-пул",
        "title": "Коллективный выкуп: G-Class (партия из 6)",
        "detail": "Прямая поставка с завода, Штутгарт",
        "roi": "—",
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYSTEM PROMPT BUILDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def build_system_prompt(
    tenant_config: dict | None = None,
    delegate: dict | None = None,
    schedule: list[dict] | None = None,
    fleet: list[dict] | None = None,
    partners: list[dict] | None = None,
    lots: list[dict] | None = None,
) -> str:
    """Assemble the full system prompt with tenant metadata and domain data.

    Parameters are optional — missing data sections are simply omitted from
    the prompt, making the concierge gracefully degrade.
    """
    delegate = delegate or DELEGATE
    schedule = schedule or SCHEDULE
    fleet = fleet or FLEET
    partners = partners or PARTNERS
    lots = lots or LOTS

    # Tenant identity
    brand = "APEX ASSET SUITE"
    event = "ADIPEC Concierge"
    support_phone = "+971500000000"
    support_username = "@appex_support"
    support_hours = "10:00–20:00 (UTC+4)"

    if tenant_config:
        brand = tenant_config.get("brand_name", brand)
        event = tenant_config.get("event_name", event)
        contact = tenant_config.get("contact", {})
        support_phone = contact.get("support_phone", support_phone)
        support_username = contact.get("support_username", support_username)
        support_hours = contact.get("support_hours", support_hours)

    # Format schedule
    schedule_text = "\n".join(
        f"  • {s['time']} — {s['title']} @ {s['place']} [{s['tag']}]"
        for s in schedule
    )

    # Format fleet
    fleet_text = "\n".join(
        f"  • {c['model']} ({c['plate']}) — водитель: {c['driver']} "
        f"(языки: {c['lang']}, тел: {c['phone']}) — ETA: {c['eta']}, статус: {c['status']}"
        for c in fleet
    )

    # Format partners
    partners_text = "\n".join(
        f"  • {p['company']} — {p['person']} ({p['title']}), {p['country']}. "
        f"Локация: {p['lounge']}, до встречи: {p['minutes_left']} мин. "
        f"Справка: {p['brief']}"
        for p in partners
    )

    # Format investment lots
    lots_text = "\n".join(
        f"  • [{l['kind']}] {l['title']} — {l['detail']}. ROI: {l['roi']}"
        for l in lots
    )

    return f"""Ты — цифровой консьерж {brand} ({event}).
Ты ассистируешь VIP-делегатам на выставке ADIPEC в Абу-Даби.
Общайся в уважительном, профессиональном тоне. Отвечай на русском языке по умолчанию,
но переключайся на язык пользователя, если он пишет на другом языке.
Будь кратким, но информативным. Используй эмодзи умеренно.

═══ ПРОФИЛЬ ДЕЛЕГАТА ═══
Имя: {delegate['name']}
Должность: {delegate['role']}
Организация: {delegate['org']}
Бейдж: {delegate['badge']}

═══ РАСПИСАНИЕ НА СЕГОДНЯ ═══
{schedule_text}

═══ АВТОПАРК (ЗАКРЕПЛЁННЫЕ АВТОМОБИЛИ) ═══
{fleet_text}

═══ B2B ПАРТНЁРЫ НА ПЛОЩАДКЕ ═══
{partners_text}

═══ ИНВЕСТИЦИОННЫЙ КАТАЛОГ ═══
{lots_text}

═══ КОНТАКТЫ ПОДДЕРЖКИ ═══
Телефон экстренной связи: {support_phone}
Telegram: {support_username}
Режим работы: {support_hours}

═══ ТВОИ ЗАДАЧИ ═══

1. РАСПИСАНИЕ И НАВИГАЦИЯ
   — Отвечай на вопросы о расписании делегата, времени и месте мероприятий.
   — Подсказывай, как добраться до VIP-лаунджей, залов и стендов.
   — Напоминай о предстоящих встречах.

2. ТРАНСФЕР И АВТОПАРК
   — Сообщай статус закреплённых автомобилей (ETA, локация, водитель).
   — Помогай с бронированием трансфера, сообщая доступные машины.
   — Передавай контактные данные водителей.

3. ИНВЕСТИЦИИ И B2B АНАЛИТИКА
   — Отвечай на вопросы по инвестиционным лотам (ROI, площадь, детали).
   — Предоставляй справки по B2B-партнёрам: их интересы, время до встречи, VIP-лаундж.
   — Если спрашивают про white paper — упомяни что аналитика подготовлена AlmaU.

4. SOS / ЭКСТРЕННАЯ ПОМОЩЬ
   — При словах «SOS», «потерял бейдж», «помогите», «экстренно», «urgent» —
     немедленно сообщи контакт координатора ({support_phone})
     и заверь, что координатор свяжется в течение 2 минут.
   — Не пытайся решить экстренные ситуации самостоятельно — эскалируй на координатора.

═══ ОГРАНИЧЕНИЯ ═══
— Не выдумывай данные. Если не знаешь ответа — скажи честно и предложи связаться с координатором.
— Не обсуждай конфиденциальные финансовые условия сделок.
— Не давай юридических или медицинских советов.
— Если вопрос не связан с ADIPEC, вежливо перенаправь к основным задачам."""
