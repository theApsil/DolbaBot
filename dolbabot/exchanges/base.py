import requests
from config import config
from utils.logger import

class ExchangeBase:
    def convert(self, from_curr: str, to_curr: str, amount: float) -> dict:
        """Абстрактный метод"""
        raise NotImplementedError


class CurrencyLayerExchange(ExchangeBase):
    BASE_URL = config.CURRENCYLAYER_URL

    def convert(self, from_curr: str, to_curr: str, amount: float) -> dict:
        """Conversion through CurrencyLayer API"""
        url = f"{self.BASE_URL}/convert"
        params = {
            "access_key": config.CURRENCYLAYER_KEY,
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
        }
        logger.info(params)
        resp = requests.get(url,  params=params, timeout=10)
        data = resp.json()

        if not data.get("success"):
            raise ValueError(f"Error CurrencyLayer API: {data.get('error', {}).get('info', ' ')}")

        return {
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "converted": data["result"],
            "rate": data["info"]["quote"],
            "timestamp": data["info"]["timestamp"],
        }