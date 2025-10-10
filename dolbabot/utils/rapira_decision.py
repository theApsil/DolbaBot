def make_decision(ask, min_volume=15000):
    if not ask:
        return None

    last_price = ask[-1]["price"]
    large_orders = [x for x in ask if x["amount"] >= min_volume]

    if large_orders:
        chosen = min(large_orders, key=lambda x: abs(x["price"] - last_price))
    else:
        chosen = max(ask, key=lambda x: x["amount"])

    return chosen
