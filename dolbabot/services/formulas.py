from utils.calculator import evaluate
from db.handlers import RegionIndexHandler

region_handler = RegionIndexHandler()

def usdt(usd: float, city: str, index: float) -> tuple[str, float]:
    city_index_obj = region_handler.get_city_index(city)
    if city_index_obj == "Москва":
        text = f"({usd} + {city}) + {index}%"
    else:
        text = f"({usd} + {city}%) + {index}%"
    return text, evaluate(text)

def jpy(usd: float, city: str, tether: float, index: float) -> tuple[str, float]:
    city_index_obj = region_handler.get_city_index(city)
    if city_index_obj == "Москва":
        text = f"({usd} + {city}) / {tether} + {index}%"
    else:
        text = f"({usd} + {city}%) / {tether} + {index}%"
    return text, evaluate(text)

def krw(usd: float, city: str, won: float, index: float) -> tuple[str, float]:
    city_index_obj = region_handler.get_city_index(city)
    if city_index_obj == "Москва":
        text = f"({usd} + {city}) / {won - 5} + {index}%"
    else:
        text = f"({usd} + {city}%) / {won - 5} + {index}%"
    return text, evaluate(text)