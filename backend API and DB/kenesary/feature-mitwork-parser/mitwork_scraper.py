# ИСТОЧНИК: eep.mitwork.kz (Евразийский электронный портал, MITWORK) -
# коммерческая площадка тендеров/закупок квазигоссектора.
#
# СТРУКТУРА САЙТА: как и goszakup.gov.kz, страница списка лотов -
# обычный серверный HTML (Yii2), без JS-рендеринга - Selenium не нужен.
# Причем, в отличие от tenderplus.kz (агрегатора, у которого поле
# "Источник" скрыто без входа), на самом mitwork.kz все поля, включая
# заказчика, полностью открыты без авторизации - проверено на карточке
# лота https://eep.mitwork.kz/ru/publics/lot/602851.
#
# ВАЖНО про НЕДВИЖИМОСТЬ: в общем каталоге (https://eep.mitwork.kz/ru/publics/lots)
# лоты - это преимущественно обычные закупки товаров/работ/услуг, как и на
# goszakup. У портала есть отдельная категория "Недвижимость" в фильтре
# слева на сайте, но на момент написания парсера не было возможности
# подтвердить ее точный URL/slug (нет прямого сетевого доступа к сайту из
# среды разработки, а в HTML категории отрисовываются без прямых ссылок,
# видимых через простой fetch). Известные по аналогии рабочие URL других
# категорий: /ru/publics/lots/equipment, /ru/publics/lots/services -
# значит и "Недвижимость" должна открываться так же, через свой slug.
#
# ЧТО СДЕЛАТЬ ПЕРЕД ЗАПУСКОМ: откройте https://eep.mitwork.kz/ru/publics/lots
# в браузере, нажмите на категорию "Недвижимость" в левом фильтре и
# скопируйте получившийся URL - подставьте его в LOTS_LIST_URL ниже.
# Пока используется общий каталог без фильтра по категории (все лоты,
# не только недвижимость) - см. также пояснение у ProcurementLotModel в
# models.py про то, почему это не место для недвижимости "по умолчанию".

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from base import BaseAppexScraper
from models import ProcurementLotModel

# ————————————————————————————————————————————————————————————————
#  Константы источника
# ————————————————————————————————————————————————————————————————

BASE_URL = "https://eep.mitwork.kz/ru/publics/lots?filter[submit]=&filter%5Bcategory%5D=1592&filter%5Blot_status%5D=EMPTY&filter%5Bis_preliminary%5D=EMPTY"

LOTS_LIST_URL = f"{BASE_URL}/ru/publics/lots"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# ————————————————————————————————————————————————————————————————
#  Парсер
# ————————————————————————————————————————————————————————————————


class MitworkScraper(BaseAppexScraper):
    """Парсер лотов с eep.mitwork.kz.

    ВНИМАНИЕ: по умолчанию собирает общий каталог лотов (товары/работы/
    услуги), а не только недвижимость - см. пояснение в шапке файла про
    LOTS_LIST_URL и подтверждение URL категории "Недвижимость"."""

    ASSET_TYPE = "PROCUREMENT"
    SOURCE = "mitwork"
    csv_filename = "mitwork_lots.csv"

    def __init__(
        self,
        tenant_id: str = "Appex_Main",
        pages_to_scan: int = 1,
        per_page: int = 50,
    ):
        super().__init__(tenant_id, pages_to_scan)
        self.per_page = per_page
        self.session: Optional[requests.Session] = None

    def _setup(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _teardown(self) -> None:
        if self.session:
            self.session.close()

    def _scrape_one_page(self, page: int) -> list:
        """Загружает одну страницу списка лотов и парсит таблицу.
        Обернуто в try/except по общей для всех парсеров логике: сбой
        одной страницы не должен ронять уже собранные данные."""
        page_results = []

        try:
            params = {"page": page, "per-page": self.per_page}
            response = self.session.get(LOTS_LIST_URL, params=params, timeout=20)
            response.raise_for_status()

            raw_rows = self._parse_lots_table(response.text)
            print(f"Страница {page}: спарсено лотов - {len(raw_rows)}")

            for raw_item in raw_rows:
                try:
                    lot = self._build_lot_model(raw_item)
                    page_results.append(lot.model_dump())
                except Exception as e:
                    print(f"Не удалось собрать модель лота {raw_item.get('lot_number')}: {e}")

        except Exception as e:
            print(f"Ошибка при обработке страницы {page}: {e}")

        return page_results

    def _parse_lots_table(self, html: str) -> list:
        """Парсит таблицу лотов со страницы списка.

        Таблица состоит из 6 колонок: Номер | Наименование |
        Дополнительная характеристика | Общая сумма, без НДС | Заказчик |
        Статус. Ищем таблицу по тексту заголовков - устойчивее к смене
        CSS-классов при обновлениях сайта, чем прямой поиск по классу.

        ПРИМЕЧАНИЕ: аналогично goszakup_scraper.py, логика построена по
        разметке, зафиксированной на момент написания, без возможности
        протестировать против живого сайта (нет сетевого доступа из
        текущей среды). Если raw_rows пустой при первом запуске - нужно
        свериться с фактическим HTML и поправить селекторы."""

        soup = BeautifulSoup(html, "html.parser")
        target_table = None

        for table in soup.find_all("table"):
            header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if any("заказчик" in h for h in header_cells) and any("статус" in h for h in header_cells):
                target_table = table
                break

        if target_table is None:
            print("Таблица лотов не найдена на странице - проверьте разметку сайта")
            return []

        rows = []
        body = target_table.find("tbody") or target_table
        for tr in body.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 6:
                continue

            lot_number = cells[0].get_text(strip=True)

            title_cell = cells[1]
            title_link = title_cell.find("a")
            title = title_link.get_text(strip=True) if title_link else title_cell.get_text(strip=True)
            source_url = self._to_abs_url(title_link.get("href") if title_link else None)

            extra_description = cells[2].get_text(strip=True)
            amount_text = cells[3].get_text(strip=True)

            customer_cell = cells[4]
            customer_link = customer_cell.find("a")
            # У ссылки на заказчика атрибут title содержит полное
            # юридическое название - оно информативнее, чем текст ссылки
            # (обычно там просто БИН/БИИН).
            customer_name = (
                customer_link.get("title", "").strip()
                if customer_link
                else customer_cell.get_text(strip=True)
            )
            customer_bin = customer_link.get_text(strip=True) if customer_link else ""

            status = cells[5].get_text(strip=True)

            rows.append(
                {
                    "lot_number": lot_number,
                    "title": title or extra_description,
                    "extra_description": extra_description,
                    "source_url": source_url,
                    "price": self._extract_number(amount_text),
                    "customer_name": customer_name,
                    "customer_bin": customer_bin,
                    "status": status,
                }
            )

        return rows

    def _build_lot_model(self, raw_item: dict) -> ProcurementLotModel:
        base_payload = self.format_to_db_payload(
            {
                "title": raw_item["title"],
                "price": raw_item["price"],
                "roi": 0.0,
                "image_url": "",
            },
            self.ASSET_TYPE,
        )

        return ProcurementLotModel(
            **base_payload,
            source=self.SOURCE,
            source_url=raw_item["source_url"],
            announcement_url=None,
            announcement_title=raw_item["extra_description"],
            lot_number=raw_item["lot_number"],
            customer_name=raw_item["customer_name"] or raw_item["customer_bin"],
            quantity=None,
            purchase_method=None,
            status=raw_item["status"],
        )

    # ————————————————————————————————————————————————————————————
    #  Вспомогательные статические методы
    # ————————————————————————————————————————————————————————————

    @staticmethod
    def _to_abs_url(href: Optional[str]) -> str:
        if not href:
            return ""
        if href.startswith("http"):
            return href
        return BASE_URL + href

    @staticmethod
    def _extract_number(text: str) -> float:
        """Достает число из строк вида '36 100 000,00 KZT' или 'не указана'."""
        if not text or "не указан" in text.lower():
            return 0.0
        cleaned = re.sub(r"[^\d.,]", "", text).replace(",", ".")
        cleaned = cleaned.strip(".")
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0


if __name__ == "__main__":
    scraper = MitworkScraper(pages_to_scan=1)
    results = scraper.run_scraper()

    print(f"\nВсего собрано лотов: {len(results)}")
    if results:
        for r in results[:3]:
            print(r)
    else:
        print("Данные не собраны - проверьте доступность сайта и структуру таблицы.")

