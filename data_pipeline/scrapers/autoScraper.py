import time
import requests
from bs4 import BeautifulSoup

from base import BaseAppexScraper


class AutoAppexScraper(BaseAppexScraper):
    """Парсер премиальных автомобилей с Kolesa.kz."""

    ASSET_TYPE = "AUTO"

    BRANDS = [
        "mercedes-benz",
        "porsche",
        "maserati"
    ]

    MAX_PAGES = 10

    def run_scraper(self) -> list:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        raw_cars = []

        for brand in self.BRANDS:

            print(f"\n========== {brand.upper()} ==========")

            for page in range(1, self.MAX_PAGES + 1):

                if page == 1:
                    url = f"https://kolesa.kz/cars/{brand}/"
                else:
                    url = f"https://kolesa.kz/cars/{brand}/?page={page}"

                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    print(f"Ошибка {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, "html.parser")

                cards = soup.find_all("div", class_="a-list__item")

                if len(cards) == 0:
                    print(f"Страница {page}: объявлений больше нет.")
                    break

                print(f"Страница {page}: найдено {len(cards)} карточек")

                for card in cards:

                    title = card.find("h5", class_="a-card__title")
                    price = card.find("span", class_="a-card__price")
                    image = card.find("img")

                    title_text = title.get_text(strip=True) if title else ""

                    price_text = price.get_text(strip=True) if price else ""
                    price_text = (
                        price_text
                        .replace("₸", "")
                        .replace("\xa0", "")
                        .replace(" ", "")
                        .replace(",", "")
                    )

                    try:
                        price_value = int(price_text)
                    except:
                        price_value = 0

                    image_url = image["src"] if image else ""

                    raw_cars.append({
                        "title": title_text,
                        "price": price_value,
                        "roi": 0.0,
                        "image_url": image_url
                    })

                time.sleep(1)

        print(f"\nДо очистки: {len(raw_cars)}")

        cleaned_cars = []

        for car in raw_cars:

            if not car["title"]:
                continue

            if car["price"] <= 0:
                continue

            if not car["image_url"]:
                continue

            cleaned_cars.append(car)

        print(f"После очистки: {len(cleaned_cars)}")

        formatted_cars = []

        for car in cleaned_cars:

            formatted_car = self.format_to_db_payload(
                raw_item=car,
                asset_type=self.ASSET_TYPE
            )

            formatted_cars.append(formatted_car)

        print(f"Готово для БД: {len(formatted_cars)}")

        return formatted_cars