# Pydantic-модели лотов для APPEX Asset Suite.

# LotModel повторяет структуру словаря, который отдает
# BaseAppexScraper.format_to_db_payload() из base.py - это нужно,
# чтобы модель и текущий пайплайн сохранения в PostgreSQL не расходились.
# RealEstateLotModel - расширение под ТЗ для источников недвижимости/
# госимущества (Goszakup, Gosreestr/e-qazyna.kz): адрес, кадастровый номер,
# площадь, статус и условия аукциона.

from typing import Optional
from pydantic import BaseModel


class LotModel(BaseModel):
    """Базовые поля, которые обязаны быть у любого лота (см. base.py)."""

    tenant_id: str
    asset_type: str  # 'PROPERTY' или 'AUTO'
    title: str
    price_usd: float
    predicted_roi: float = 0.0
    image_url: str
    created_at: str


class RealEstateLotModel(LotModel):
    """Расширение под лоты недвижимости/госимущества."""

    source: str  # "goszakup" | "gosreestr" - откуда пришел лот
    source_url: Optional[str] = None
    lot_number: Optional[str] = None
    status: Optional[str] = None  # текстовый статус: "Прием заявок", "Торги завершены" и т.д.
    auction_start_date: Optional[str] = None  # дата и время начала торгов, как на сайте: "18.02.2026 10:00"

    address: Optional[str] = None  # адрес объекта
    cadastral_number: Optional[str] = None  # кадастровый номер
    area_sqm: Optional[float] = None  # площадь объекта, кв.м
    auction_conditions: Optional[str] = None  # шаг аукциона, размер задатка и т.п.


class ProcurementLotModel(LotModel):
    """Лот обычных госзакупок товаров/работ/услуг с goszakup.gov.kz.

    ВАЖНО: это НЕ недвижимость. Реестр лотов на goszakup.gov.kz - это
    закупки товаров/работ/услуг (канцелярия, техника, ремонт и т.п.), а не
    продажа/аренда госимущества. Модель сохраняет эти данные отдельно от
    RealEstateLotModel, чтобы не смешивать разные по смыслу типы лотов.
    """

    source: str = "goszakup"
    source_url: Optional[str] = None  # ссылка на карточку лота (subpriceoffer)
    announcement_url: Optional[str] = None  # ссылка на объявление, в которое входит лот
    announcement_title: Optional[str] = None  # название объявления
    lot_number: Optional[str] = None  # № лота, например "82692058-ОИ2"
    customer_name: Optional[str] = None  # заказчик
    quantity: Optional[float] = None  # количество/объем закупки
    purchase_method: Optional[str] = None  # способ закупки: "Запрос ценовых предложений" и т.п.
    status: Optional[str] = None  # статус лота: "Опубликован", "Опубликован (прием заявок)" и т.п.

