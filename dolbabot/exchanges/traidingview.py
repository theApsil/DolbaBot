import requests
from config import config


def get_courses_from_tv():
    response = requests.get(config.TRAIDINGVIEW_FASTAPI_APP_LINK)
    response.raise_for_status()
    data = response.json()
    return data
