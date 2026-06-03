import re
from dataclasses import dataclass
from telegram import Update

from db.handlers import region_index_handler
from .constants import Msg


PAIR_RE = re.compile(r"^[A-Za-z]{6}$")


@dataclass
class CityIndex:
    city: str
    index: float


async def parse_city_index(
    update: Update,
    city_arg: str | None,
    index_arg: str | None,
) -> CityIndex | None:
    """Парсит город и индекс из аргументов. На ошибках сам отвечает пользователю."""
    if not city_arg:
        await update.message.reply_text(Msg.CITY_REQUIRED, parse_mode="Markdown")
        return None

    city = city_arg.title()
    if not region_index_handler.get_one(city=city):
        await update.message.reply_text(
            Msg.CITY_NOT_FOUND.format(city=city), parse_mode="Markdown"
        )
        return None

    if index_arg is None:
        await update.message.reply_text(Msg.INDEX_REQUIRED, parse_mode="Markdown")
        return None

    try:
        return CityIndex(city, float(index_arg))
    except ValueError:
        await update.message.reply_text(Msg.INDEX_NOT_NUMBER)
        return None


def parse_pair(raw: str) -> tuple[str, str] | None:
    """'eurusd' / 'EURUSD' → ('EUR', 'USD'). None, если невалидно."""
    clean = re.sub(r"[^A-Za-z]", "", raw).upper()
    if len(clean) < 6:
        return None
    return clean[:3], clean[3:6]