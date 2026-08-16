# ИСТОЧНИК: формально портал остается gosreestr.kz, но официальной точкой доступа к реестру и
# торгам сайт e-qazyna.kz - именно туда gosreestr.kz сейчас
# автоматически перенаправляет пользователя. Публичный (без авторизации)
# раздел торгов - sauda.e-qazyna.kz. Поэтому парсер целится в него.

import os
import re
import time
from random import uniform

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from base import BaseAppexScraper
from models import RealEstateLotModel

# ————————————————————————————————————————————————————————————————
#  Константы источника
# ————————————————————————————————————————————————————————————————


LOTS_LIST_URL = "https://sauda.e-qazyna.kz/ru/list?objectType=RealEstate&searchStatus=ApplicationsAccept&auctionNumber=&textRu=&moreFilters=off&sellerBin=&startDateFromInclusive=&startDateToInclusive=&publishDateFromInclusive=&publishDateToInclusive=&submitFilters=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8"

# Префиксы категорий, под которыми на сайте идет недвижимость
REAL_ESTATE_PREFIXES = (
    "Недвижимость:",
    "Недвижимость (Незавершенное строительство):",
)

# Файл, в который построчно сохраняются результаты
CSV_FILENAME = "gosreestr_lots.csv"

# ————————————————————————————————————————————————————————————————
#  Локаторы элементов на странице 
# ————————————————————————————————————————————————————————————————

LOCATOR_LOT_CARD_LINK = (By.CSS_SELECTOR, "a[href^='/ru/list/']")
LOCATOR_LOT_TITLE = (By.CSS_SELECTOR, "div.col-12 > div.font-16.font-weight-900.text-dark.lh-sm")
LOCATOR_LOT_PRICE = (By.XPATH, "//p[contains(., 'Стартовая цена')]//span[contains(@class,'text-primary')]")
LOCATOR_LOT_ADDRESS = (By.XPATH, "//p[contains(text(),'Расположение объекта')]/following-sibling::p")
LOCATOR_LOT_STATUS = (By.XPATH, "//div[contains(., 'Статус торгов:')]/span")
LOCATOR_LOT_OBJECT_INFO = (By.XPATH,"//p[(contains(text(),'Объект продажи') or contains(text(),'Объект аренды'))]/following-sibling::p")
LOCATOR_LOT_IMAGE = (By.CSS_SELECTOR, "img.img-curr-item")

# ————————————————————————————————————————————————————————————————
#  Вспомогательные функции 
# ————————————————————————————————————————————————————————————————

def init_driver() -> webdriver.Chrome:
    """Поднимает headless Chrome."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def human_delay(min_seconds: float = 2, max_seconds: float = 4) -> None:
    """Имитация паузы между действиями."""
    time.sleep(uniform(min_seconds, max_seconds))


def save_to_csv(rows: list, filename: str = CSV_FILENAME) -> None:
    """Дозаписывает строки в CSV.

    Вызывается после каждой страницы, а не один раз в самом конце,
    если парсер упадет на середине работы, уже собранные данные все равно останутся на диске, а не потеряются."""
    if not rows:
        return

    file_already_exists = os.path.exists(filename)
    df = pd.DataFrame(rows)
    df.to_csv(filename, mode="a", header=not file_already_exists, index=False, encoding="utf-8-sig")
    print(f"В {filename} записано строк: {len(rows)}")


# ————————————————————————————————————————————————————————————————
#  Парсер
# ————————————————————————————————————————————————————————————————

class GosreestrScraper(BaseAppexScraper):
    """Парсер лотов недвижимости с торговой площадки e-qazyna.kz."""

    ASSET_TYPE = "PROPERTY"
    SOURCE = "gosreestr"

    def __init__(self, tenant_id: str = "Appex_Main", pages_to_scan: int = 1):
        super().__init__(tenant_id)
        self.pages_to_scan = pages_to_scan

    def run_scraper(self) -> list:
        # Начинаем каждый запуск с чистого CSV-файла, чтобы старые
        # результаты из прошлого запуска не перемешивались с новыми.
        if os.path.exists(CSV_FILENAME):
            os.remove(CSV_FILENAME)

        all_results = []
        driver = init_driver()

        try:
            for page in range(1, self.pages_to_scan + 1):
                page_results = self._scrape_one_page(driver, page)
                save_to_csv(page_results)
                all_results.extend(page_results)
        finally:
            driver.quit()

        return all_results

    def _scrape_one_page(self, driver, page: int) -> list:
        """Открывает одну страницу списка и парсит все лоты недвижимости
        с нее. Обернуто в try/except, чтобы ошибка на одной странице
        (например, сайт не ответил) не обрушила уже собранные данные
        с предыдущих страниц."""
        page_results = []

        try:
            page_url = f"{LOTS_LIST_URL}&p={page}"
            driver.get(page_url)
            human_delay()

            cards = self._collect_lot_cards(driver)
            real_estate_cards = [c for c in cards if any(prefix.lower() in c["title_raw"].lower() for prefix in REAL_ESTATE_PREFIXES)]
            print(f"Страница {page}: всего лотов - {len(cards)}, из них недвижимость - {len(real_estate_cards)}")

            for card in real_estate_cards:
                try:
                    raw_item = self._parse_lot_page(driver, card["url"])
                    lot = self._build_lot_model(raw_item)
                    page_results.append(lot.model_dump())
                except Exception as e:
                    print(f"Не удалось спарсить лот {card['url']}: {e}")
                human_delay(1, 2)

        except Exception as e:
            print(f"Ошибка при обработке страницы {page}: {e}")

        return page_results

    def _collect_lot_cards(self, driver) -> list:
        """Собирает со страницы списка ссылку и текст названия каждого
        лота. Текст нужен, чтобы понять, недвижимость это или нет, не
        открывая каждую карточку по отдельности."""
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(LOCATOR_LOT_CARD_LINK))
        except Exception:
            print("Лоты не загрузились на странице списка")
            return []

        cards = {}
        for element in driver.find_elements(*LOCATOR_LOT_CARD_LINK):
            href = element.get_attribute("href")
            title_raw = element.text.strip()

            # У каждой карточки на сайте есть 2 ссылки с одинаковым href:
            # одна оборачивает картинку (текста нет), другая - название
            # лота (текст есть). Нам нужна только вторая.
            if href and title_raw:
                cards[href] = title_raw

        return [{"url": url, "title_raw": title} for url, title in cards.items()]

    def _parse_lot_page(self, driver, url: str) -> dict:
        """Открывает карточку лота и вытаскивает поля."""
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(LOCATOR_LOT_TITLE))

        price_text = self._safe_find_text(driver, LOCATOR_LOT_PRICE)
        object_info_text = self._safe_find_text(driver, LOCATOR_LOT_OBJECT_INFO)
        page_text = self._safe_find_text(driver, (By.TAG_NAME, "body"))

        return {
            "title": self._safe_find_text(driver, LOCATOR_LOT_TITLE),
            "price": self._extract_number(price_text),
            "address": self._safe_find_text(driver, LOCATOR_LOT_ADDRESS),
            "cadastral_number": self._extract_cadastral_number(object_info_text),
            "area_sqm": self._extract_area(object_info_text),
            "status": self._safe_find_text(driver, LOCATOR_LOT_STATUS),
            "auction_conditions": object_info_text,
            "source_url": url,
            "image_url": self._safe_find_lot_image(driver, url),
            "lot_number": self._extract_lot_number(page_text),
            "auction_start_date": self._extract_auction_start_date(page_text),
        }

    def _build_lot_model(self, raw_item: dict) -> RealEstateLotModel:
        """Собирает Pydantic-модель лота из сырых данных со страницы."""
        base_payload = self.format_to_db_payload(
            {
                "title": raw_item["title"],
                "price": raw_item["price"],
                "roi": 0.0,
                "image_url": raw_item["image_url"],
            },
            self.ASSET_TYPE,
        )

        return RealEstateLotModel(
            **base_payload,
            source=self.SOURCE,
            source_url=raw_item["source_url"],
            lot_number=raw_item["lot_number"],
            status=raw_item["status"],
            address=raw_item["address"],
            cadastral_number=raw_item["cadastral_number"],
            area_sqm=raw_item["area_sqm"],
            auction_conditions=raw_item["auction_conditions"],
            auction_start_date=raw_item["auction_start_date"],
        )

    # ————————————————————————————————————————————————————————————
    #  Вспомогательные статические методы
    # ————————————————————————————————————————————————————————————

    @staticmethod
    def _safe_find_text(driver, locator: tuple) -> str:
        """Возвращает текст элемента по локатору (CSS или XPath), либо
        пустую строку, если элемент не найден. Нужно, чтобы один
        отсутствующий блок на странице не ронял весь парсер."""
        try:
            return driver.find_element(*locator).text.strip()
        except Exception:
            return ""

    @staticmethod
    def _extract_number(text: str) -> float:
        """Достает число из строки вида '12 500 000 тг' или '149 811 476,00'."""
        if not text:
            return 0.0
        cleaned = re.sub(r"[^\d.]", "", text.replace(",", "."))
        cleaned = cleaned.strip(".")
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def _extract_area(text: str) -> float:
        """
        Приоритет:
        1. Общая площадь, кв.м.
        2. Площадь: ... кв.м.
        3. Общей площадью ... кв.м.
        4. Площадь земельного участка ... га (переводится в кв.м.)
        """

        if not text:
            return 0.0

        patterns = [
            (r"общей\s+площадью.*?-\s*([\d.,]+)", 1.0),

            (r"общей\s+площадью[:\s]*([\d.,]+)\s*кв", 1.0),

            (r"площадь[:\s]*([\d.,]+)\s*кв", 1.0),

            (r"общей\s+площадью\s*([\d.,]+)\s*кв", 1.0),

            (r"площадь.*?га.*?-\s*([\d.,]+)", 10000.0),

            (r"площадь[:\s]*([\d.,]+)\s*га", 10000.0),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if not match:
                continue

            try:
                value = float(match.group(1).replace(",", "."))
                return round(value * multiplier, 2)
            except ValueError:
                continue

        return 0.0
    
    @staticmethod
    def _extract_cadastral_number(text: str) -> str:
        """Извлекает кадастровый номер из текстового описания объекта."""
        if not text:
            return ""

        # [^\s;,.]+ вместо \S+ - иначе в номер попадает точка с запятой
        # или запятая, идущая сразу после него в тексте описания
        match = re.search(r"кадастровый номер[:\s-]*([^\s;,.]+)", text, re.IGNORECASE)
        return match.group(1) if match else ""

    @staticmethod
    def _safe_find_lot_image(driver, current_url: str) -> str:
        """Ищет фото именно текущего лота, а не "похожего" лота из
        виджета в футере страницы (см. пояснение у LOCATOR_LOT_IMAGE)."""

        lot_id = current_url.rstrip("/").split("/")[-1]

        try:
            images = driver.find_elements(*LOCATOR_LOT_IMAGE)
        except Exception:
            return ""

        for img in images:
            src = img.get_attribute("src") or ""
            if not src or "no-photo" in src.lower():
                continue

            try:
                href = img.find_element(By.XPATH, "./ancestor::a[1]").get_attribute("href") or ""
            except Exception:
                # картинка не обёрнута в ссылку - не похоже на карточку
                # из футера, считаем её своей
                href = current_url

            if lot_id not in href:
                continue  # это фото другого (рекомендованного) лота

            return src

        return ""

    @staticmethod
    def _extract_lot_number(page_text: str) -> str:
        """Достает номер лота вида '№ 430337' из текста страницы.

        ВАЖНО: ищем "№" только в начале строки (после переноса),
        так в тексте страницы отделен номер лота от заголовка, и
        требуем минимум 4 цифры - номер лота на сайте шестизначный
        ,а номер квартиры/паркоместа - максимум 2-3 цифры."""

        if not page_text:
            return ""
        match = re.search(r"\n№\s*(\d{4,})", page_text)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_auction_start_date(page_text: str) -> str:
        """Достает дату+время начала торгов вида '18.02.2026 10:00'
        из текста после 'Начало торгов'."""
        if not page_text:
            return ""
        match = re.search(r"Начало торгов\s+(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})", page_text)
        return match.group(1) if match else ""

if __name__ == "__main__":
    scraper = GosreestrScraper(pages_to_scan=1)
    results = scraper.run_scraper()

    print(f"\nВсего собрано лотов недвижимости: {len(results)}")
    if results:
        for r in results[:3]:
            print(r)
    else:
        print("Данные не собраны - проверьте доступность сайта и локаторы.")