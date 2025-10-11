from utils.calculator import evaluate

def usdt(usd: float, city: float, index: float) -> tuple[str, float]:
    text = f"({usd} + {city}%) + {index}%"
    return text, evaluate(text)

def jpy(usd: float, city: float, tether: float, index: float) -> tuple[str, float]:
    text = f"({usd} + {city}%) / {tether} + {index}%"
    print(text)
    return text, evaluate(text)

def krw(usd: float, city: float, won: float, index: float) -> tuple[str, float]:
    text = f"({usd} + {city}%) / {won - 5} + {index}%"
    return text, evaluate(text)