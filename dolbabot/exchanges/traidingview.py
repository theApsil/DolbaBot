import requests
from config import TRAIDINGVIEW_FASTAPI_APP_LINK


def get_courses_from_tv():
    response = requests.get(TRAIDINGVIEW_FASTAPI_APP_LINK)
    response.raise_for_status()
    data = response.json()
    return data
