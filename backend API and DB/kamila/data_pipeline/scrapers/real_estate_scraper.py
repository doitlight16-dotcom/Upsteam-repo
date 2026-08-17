from base import BaseAppexScraper

class RealEstateScraper(BaseAppexScraper):
    """Парсер для сбора данных о недвижимости в Абу-Даби. В реальном проекте это будет парсер для сбора данных 
    о недвижимости в Абу-Даби. В данном примере это имитация, возвращающая жестко заданные (хардкоженные) данные."""

    ASSET_TYPE = "PROPERTY"

    def run_scraper(self) -> list:
        """Запускает процесс сбора данных о недвижимости."""
        # TODO: заменить на реальный парсер, который будет собирать данные о недвижимости в Абу-Даби
        raw_items =  [{
            "title": "",
            "price": 0.0,
            "roi": 0.0,
            "image_url": ""
        }, 
        {
            "title": "",
            "price": 0.0,
            "roi": 0.0,
            "image_url": ""
        }
        ]

        payload = []

        for item in raw_items:
            payload.append(self.format_to_db_payload(item, self.ASSET_TYPE))
        return payload
