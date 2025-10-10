from utils.calculator import evaluate

def tether(usdt: float, city: float, index: float) -> tuple[str, float]:
    text = f"({usdt} + {city}%) + {index}%"
    return text, evaluate(text)

def jpy(usdt: float, city: float, tether: float, index: float) -> tuple[str, float]:
    text = f"({usdt} + {city}%) / {tether} + {index}%"
    print(text)
    return text, evaluate(text)

def krw(usdt: float, city: float, won: float, index: float) -> tuple[str, float]:
    text = f"({usdt} + {city}%) / {won - 5} + {index}%"
    return text, evaluate(text)