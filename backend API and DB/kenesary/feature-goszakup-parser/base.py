from abc import ABC, abstractmethod
import datetime

class BaseAppexScraper(ABC):
    def __init__(self, tenant_id: str = "Appex_Main"):
        self.tenant_id = tenant_id

    @abstractmethod
    def run_scraper(self) -> list:
        """Метод должен быть переопределен в дочерних классах"""
        pass

    def format_to_db_payload(self, raw_item: dict, asset_type: str) -> dict:
        """Приведение сырых данных к единому стандарту PostgreSQL"""
        return {
            "tenant_id": self.tenant_id,
            "asset_type": asset_type,  # 'PROPERTY' или 'AUTO'
            "title": raw_item.get("title", "No Title").strip(),
            "price_usd": float(raw_item.get("price", 0.0)),
            "predicted_roi": float(raw_item.get("roi", 0.0)),
            "image_url": raw_item.get("image_url", "https://appex.suite"),
            "created_at": datetime.datetime.utcnow().isoformat()

        }
