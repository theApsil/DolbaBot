import bs4

class CourseParser:
    def __init__(self):
        pass

    def _format_number(self, string: str) -> float | None:
        string = string.strip()
        string = string.replace(",", ".")
        string = "".join(string.split())

        try:
            result = float(string)
        except ValueError:
            result = None

        return result


    def get_course(self, data):
        soup = bs4.BeautifulSoup(data, features="html.parser")

        for sell_order_button in soup.find_all("div", attrs={"data-name": "sell-order-button"}):
            for price_candidate in sell_order_button.find_all("span"):
                if price := self._format_number(price_candidate.text):
                    return price
        return None

parser = CourseParser()