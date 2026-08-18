# ИСТОЧНИК: goszakup.gov.kz - портал государственных закупок РК.
#
# ВАЖНО #1: реестр лотов на этом портале - это обычные закупки товаров,
# работ и услуг (канцелярия, техника, стройматериалы, ремонтные работы и
# т.п.), а НЕ продажа/аренда недвижимости или госимущества. Для
# недвижимости в РК используется другой источник - gosreestr/e-qazyna.kz
# (см. gosreestr_scraper.py). Здесь лоты сохраняются как есть, отдельным
# типом ProcurementLotModel, чтобы не смешивать с недвижимостью.
#
# ВАЖНО #2: страница https://goszakup.gov.kz/ru/search/lots рендерится на
# сервере (обычный HTML в ответе, не SPA/JS), поэтому в отличие от
# gosreestr здесь НЕ нужен Selenium - хватает requests + BeautifulSoup.
# Пагинация - через query-параметры count_record/page в URL.
#
# ОГРАНИЧЕНИЕ ИСТОЧНИКА: сайт показывает не более 10000 записей в базовом
# поиске без доп. фильтров (200 страниц по 50 записей) - это ограничение
# самого сайта, а не парсера.

import os
import re
import time
from random import uniform
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

from base import BaseAppexScraper
from models import ProcurementLotModel

# ————————————————————————————————————————————————————————————————
#  Константы источника
# ————————————————————————————————————————————————————————————————

BASE_URL = "https://goszakup.gov.kz"
LOTS_LIST_URL = f"{BASE_URL}/ru/search/lots"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

CSV_FILENAME = "goszakup_lots.csv"

# ————————————————————————————————————————————————————————————————
#  Вспомогательные функции
# ————————————————————————————————————————————————————————————————


def human_delay(min_seconds: float = 1.5, max_seconds: float = 3.0) -> None:
    """Имитация паузы между запросами страниц."""
    time.sleep(uniform(min_seconds, max_seconds))


def save_to_csv(rows: list, filename: str = CSV_FILENAME) -> None:
    """Дозаписывает строки в CSV после каждой страницы (см. пояснение в
    gosreestr_scraper.py - тот же принцип: не терять уже собранное, если
    парсер упадет на середине)."""
    if not rows:
        return

    file_already_exists = os.path.exists(filename)
    df = pd.DataFrame(rows)
    df.to_csv(filename, mode="a", header=not file_already_exists, index=False, encoding="utf-8-sig")
    print(f"В {filename} записано строк: {len(rows)}")


# ————————————————————————————————————————————————————————————————
#  Парсер
# ————————————————————————————————————————————————————————————————


class GoszakupScraper(BaseAppexScraper):
    """Парсер реестра лотов (товары/работы/услуги) с goszakup.gov.kz.

    ВНИМАНИЕ: это НЕ недвижимость - см. пояснение в шапке файла."""

    ASSET_TYPE = "PROCUREMENT"
    SOURCE = "goszakup"

    def __init__(
        self,
        tenant_id: str = "Appex_Main",
        pages_to_scan: int = 1,
        records_per_page: int = 50,
    ):
        super().__init__(tenant_id)
        self.pages_to_scan = pages_to_scan
        self.records_per_page = records_per_page
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def run_scraper(self) -> list:
        if os.path.exists(CSV_FILENAME):
            os.remove(CSV_FILENAME)

        all_results = []
        for page in range(1, self.pages_to_scan + 1):
            page_results = self._scrape_one_page(page)
            save_to_csv(page_results)
            all_results.extend(page_results)
            human_delay()

        return all_results

    def _scrape_one_page(self, page: int) -> list:
        """Загружает одну страницу реестра лотов и парсит таблицу.
        Обернуто в try/except по той же логике, что и в gosreestr_scraper -
        сбой одной страницы не должен ронять уже собранные данные."""
        page_results = []

        try:
            params = {"count_record": self.records_per_page, "page": page}
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
        """Парсит основную таблицу лотов со страницы поиска.

        Таблица состоит из 7 колонок: № лота | Наименование объявления
        (+ Заказчик) | Наименование и описание лота | Кол-во | Сумма, тг. |
        Способ закупки | Статус.

        Ищем таблицу по содержимому заголовков (а не по CSS-классу) - на
        Yii2-вёрстке классы могут отличаться между версиями/окружениями
        сайта, а текст заголовков стабильнее.

        ПРИМЕЧАНИЕ: селекторы построены по разметке, зафиксированной на
        момент написания парсера, без возможности протестировать против
        живого сайта (нет доступа из текущей среды). При первом запуске
        стоит проверить, что raw_rows не пустой - если структура таблицы
        на сайте изменилась, нужно будет поправить логику ниже."""

        soup = BeautifulSoup(html, "html.parser")
        target_table = None

        for table in soup.find_all("table"):
            header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if any("лота" in h for h in header_cells) and any("способ закупки" in h for h in header_cells):
                target_table = table
                break

        if target_table is None:
            print("Таблица лотов не найдена на странице - проверьте разметку сайта")
            return []

        rows = []
        body = target_table.find("tbody") or target_table
        for tr in body.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 7:
                continue

            lot_number = cells[0].get_text(strip=True)

            announce_cell = cells[1]
            announce_link = announce_cell.find("a")
            announcement_title = announce_link.get_text(strip=True) if announce_link else ""
            announcement_url = self._to_abs_url(announce_link.get("href") if announce_link else None)
            customer_name = self._extract_customer(announce_cell)

            item_cell = cells[2]
            item_link = item_cell.find("a")
            item_title = item_link.get_text(strip=True) if item_link else item_cell.get_text(strip=True)
            source_url = self._to_abs_url(item_link.get("href") if item_link else None)

            quantity_text = cells[3].get_text(strip=True)
            amount_text = cells[4].get_text(strip=True)
            purchase_method = cells[5].get_text(strip=True)
            status = cells[6].get_text(strip=True)

            rows.append(
                {
                    "lot_number": lot_number,
                    "announcement_title": announcement_title,
                    "announcement_url": announcement_url,
                    "customer_name": customer_name,
                    "title": item_title or announcement_title,
                    "source_url": source_url or announcement_url,
                    "quantity": self._extract_number(quantity_text),
                    "price": self._extract_number(amount_text),
                    "purchase_method": purchase_method,
                    "status": status,
                }
            )

        return rows

    def _build_lot_model(self, raw_item: dict) -> ProcurementLotModel:
        """Собирает Pydantic-модель лота из сырых данных таблицы.

        ПРИМЕЧАНИЕ по price_usd: сумма закупки на сайте указана в тенге, но
        по той же логике, что и в gosreestr_scraper.py (там тоже кладут
        цену в тенге в price_usd без конвертации), сумма кладется в
        price_usd как есть, без пересчета в доллары. Если конвертация
        нужна - ее стоит делать одним отдельным шагом для всех источников
        сразу, а не внутри каждого парсера по отдельности."""

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
            announcement_url=raw_item["announcement_url"],
            announcement_title=raw_item["announcement_title"],
            lot_number=raw_item["lot_number"],
            customer_name=raw_item["customer_name"],
            quantity=raw_item["quantity"],
            purchase_method=raw_item["purchase_method"],
            status=raw_item["status"],
        )

    # ————————————————————————————————————————————————————————————
    #  Вспомогательные статические методы
    # ————————————————————————————————————————————————————————————

    @staticmethod
    def _to_abs_url(href: Optional[str]) -> str:
        """Достраивает относительную ссылку сайта до абсолютной."""
        if not href:
            return ""
        if href.startswith("http"):
            return href
        return BASE_URL + href

    @staticmethod
    def _extract_customer(cell) -> str:
        """В ячейке объявления после ссылки на объявление на сайте идет
        текст вида 'Заказчик: <название>'. Достаем его из полного текста
        ячейки регуляркой."""
        full_text = cell.get_text(" ", strip=True)
        match = re.search(r"Заказчик:\s*(.+)", full_text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_number(text: str) -> float:
        """Достает число из строк вида '1 675 599.00' или '5.5'."""
        if not text:
            return 0.0
        cleaned = re.sub(r"[^\d.,]", "", text).replace(",", ".")
        cleaned = cleaned.strip(".")
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0


if __name__ == "__main__":
    scraper = GoszakupScraper(pages_to_scan=1)
    results = scraper.run_scraper()

    print(f"\nВсего собрано лотов: {len(results)}")
    if results:
        for r in results[:3]:
            print(r)
    else:
        print("Данные не собраны - проверьте доступность сайта и структуру таблицы.")
