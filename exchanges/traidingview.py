import bs4
import requests


def format_number(string: str) -> float | None:
    string = string.strip()
    string = string.replace(",", ".")
    string = "".join(string.split())

    try:
        result = float(string)
    except ValueError:
        result = None

    return result

def get_courses_from_tv():
    response = requests.get("https://tradingview-generate.xottab-ops.ru/page")
    response.raise_for_status()

    data = response.json()
    html_data = data["html"]

    soup = bs4.BeautifulSoup(html_data, features="html.parser")

    for sell_order_button in soup.find_all("div", attrs={"data-name": "sell-order-button"}):
        for price_candidate in sell_order_button.find_all("span"):
            if price := format_number(price_candidate.text):
                return price