import re
from config import EXCEL_PATH
import pandas as pd

def escape_md(text: str) -> str:
    """
    Экранирует спецсимволы MarkdownV2 для Telegram
    """
    text = str(text) if text is not None else ""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


def read_excel(path=EXCEL_PATH):
    df = pd.read_excel(path)

    result = {}
    for _, row in df.iterrows():
        city = str(row['Город']).strip().lower()
        index = float(str(row['Индекс']).replace(',', '.'))
        result[city] = (city, index)

    return result

if __name__ == "__main__":
    dct = read_excel()
    print(dct)