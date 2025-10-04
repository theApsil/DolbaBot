import requests
import json


def get_courses_from_grinex(url="https://grinex.io/api/v1/spot/depth?symbol=usdta7a5"):
    response = requests.get()
    result = json.loads(response.text)

    ask = result['asks'][0:5]
    bid = result['bids']
    return ask, bid
