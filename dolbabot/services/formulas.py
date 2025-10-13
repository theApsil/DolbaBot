from utils.calculator import evaluate
from db.handlers import RegionIndexHandler

region_handler = RegionIndexHandler()

def usdt(usd: float, city: str, index: float) -> str | tuple[str, float]:
    city_index_obj = region_handler.get_city_index(city)
    if city_index_obj.city == "Москва":
        text = f"({usd} + {city_index_obj.index}) + {index}%"
    elif city_index_obj is not None:
        text = f"({usd} + {city_index_obj.index}%) + {index}%"
    else:
        return "Несуществующий город. Введите корректный город."
    return text, evaluate(text)

def jpy(usd: float, city: str, tether: float, index: float) -> str | tuple[str, float]:
    city_index_obj = region_handler.get_city_index(city)
    if city_index_obj.city == "Москва":
        text = f"({usd} + {city_index_obj.index}) / {tether} + {index}%"
    elif city_index_obj is not None:
        text = f"({usd} + {city_index_obj.index}%) / {tether} + {index}%"
    else:
        return "Несуществующий город. Введите корректный город."
    return text, evaluate(text)

def krw(usd: float, city: str, won: float, index: float) -> str | tuple[str, float]:
    city_index_obj = region_handler.get_city_index(city)
    if city_index_obj.city == "Москва":
        text = f"({usd} + {city_index_obj.index}) / {won - 5} + {index}%"
    elif city_index_obj is not None:
        text = f"({usd} + {city_index_obj.index}%) / {won - 5} + {index}%"
    else:
        return "Несуществующий город. Введите корректный город."
    return text, evaluate(text)