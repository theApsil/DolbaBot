import requests
import json
from config import config


def get_courses_from_grinex(url=config.GRINEX_URL):
    response = requests.get(url)
    result = json.loads(response.text)

    ask = result['asks'][0:5]
    bid = result['bids'][0]['price']
    return ask[::-1], bid

def normalize_grinex_data(data):
    lines = []

    for item in data:
        price = float(item['price'])
        amount = float(item['volume'])

        formatted_price = f"{price:.2f}"
        formatted_amount = f"{amount:.2f}"

        line = f"{formatted_price}\t {formatted_amount}"
        lines.append(line)

    return "\n".join(lines)