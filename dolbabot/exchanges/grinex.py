import requests
import json


def get_courses_from_grinex(url="https://grinex.io/api/v1/spot/depth?symbol=usdta7a5"):
    response = requests.get(url)
    result = json.loads(response.text)

    ask = result['asks'][0:5]
    bid = result['bids'][0]['price']
    return ask, bid

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