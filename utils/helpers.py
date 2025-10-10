import re

def escape_md(text: str) -> str:
    """
    Экранирует спецсимволы MarkdownV2 для Telegram
    """
    text = str(text) if text is not None else ""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)
