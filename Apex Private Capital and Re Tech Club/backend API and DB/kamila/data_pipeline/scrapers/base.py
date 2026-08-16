from abc import ABC, abstractmethod
import datetime


class BaseAppexScraper(ABC):

    def __init__(self, tenant_id: str = "Appex_Main"):
        self.tenant_id = tenant_id

    @abstractmethod
    def run_scraper(self) -> list:
        """Метод должен быть переопределен в дочерних классах."""
        pass

    def format_to_db_payload(
        self,
        raw_item: dict,
        asset_type: str
    ) -> dict:
        """
        Приведение сырых данных к единому стандарту.
        
        Цена из Kolesa приходит в KZT.
        Дополнительно сохраняем цену в USD.
        """

        price_kzt = float(
            raw_item.get("price", 0.0)
        )

        # Текущий курс для нашего тестового расчета.
        # 1 USD = 540 KZT
        usd_rate = 540

        price_usd = round(
            price_kzt / usd_rate,
            2
        )

        return {
            "tenant_id": self.tenant_id,

            "asset_type": asset_type,

            "title": raw_item.get(
                "title",
                "No Title"
            ).strip(),

            # Цена в обеих валютах
            "price_kzt": price_kzt,
            "price_usd": price_usd,

            # Год выпуска автомобиля
            "year": raw_item.get("year"),

            # ROI из исходных данных
            "predicted_roi": float(
                raw_item.get("roi", 0.0)
            ),

            "image_url": raw_item.get(
                "image_url",
                "https://appex.suite"
            ),

            "created_at": datetime.datetime.utcnow().isoformat()
        }