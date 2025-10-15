import requests
import json


def get_courses_from_rapira(url="https://api.rapira.net/market/exchange-plate-mini"):
    response = requests.post(url,
                             headers={"Content-Type": "application/x-www-form-urlencoded"},
                             data="symbol=USDT/RUB")
    response.raise_for_status()
    result = json.loads(response.text)
    ask = result['ask']['items']
    bid = result['bid']['items'][0]['price']
    return ask[0:10][::-1], bid


def normalize_rapira_data(data):
    lines = []

    for item in data:
        price = float(item['price'])
        amount = float(item['amount'])

        formatted_price = f"{price:.2f}"
        formatted_amount = f"{amount:.2f}"

        line = f"{formatted_price}\t {formatted_amount}"
        lines.append(line)

    return "\n".join(lines)