import requests
from config import XE_API_USER, XE_API_KEY


class ExchangeBase:
    def convert(self, from_curr: str, to_curr: str, amount: float) -> dict:
        """Абстрактный метод"""
        raise NotImplementedError


class XEExchange(ExchangeBase):
    BASE_URL = "https://xecdapi.xe.com/v1/convert_from.json"

    def convert(self, from_curr: str, to_curr: str, amount: float) -> dict:
        """Конвертация валют через XE API"""
        params = {
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
        }
        resp = requests.get(
            self.BASE_URL,
            params=params,
            auth=(XE_API_USER, XE_API_KEY),
            timeout=10
        )
        data = resp.json()

        if "to" not in data:
            raise ValueError(f"Ошибка XE API: {data}")

        rate_info = data["to"][0]
        return {
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "converted": rate_info["mid"],
            "rate": rate_info["mid"] / amount if amount != 0 else rate_info["mid"],
            "timestamp": data.get("timestamp"),
        }
