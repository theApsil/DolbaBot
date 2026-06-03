from telegram import Update
from telegram.ext import ContextTypes

from exchanges.base import CurrencyLayerExchange
from exchanges.grinex import get_courses_from_grinex
from exchanges.rapira import get_courses_from_rapira
from exchanges.traidingview import get_courses_from_tv

from services.formulas import usdt, krw, jpy
from utils.calculator import evaluate
from utils.logger import logger
from utils.rapira_decision import make_decision

from ..constants import CB, Msg
from ..formatters import (
    format_all_rates_md_v2, format_usdt_rub, format_rub_usdt,
    format_won, format_pair, utc_from_iso, utc_from_ts, utc_now,
)
from ..keyboards import refresh_all_kb, refresh_simple_kb, refresh_pair_kb
from ..parsers import parse_city_index, parse_pair


exchange = CurrencyLayerExchange()


# ============== /курс ==============

async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]

    r_ask, r_bids = get_courses_from_rapira()
    actual_tether = make_decision(r_ask)["price"]
    logger.info(f"DECISION RAPIRA: {actual_tether}")
    r_ask_top = r_ask[5:10]

    # /курс  → всё сразу
    if not args:
        await _all_rates(update, r_ask_top, r_bids)
        return

    arg = args[0].lower()

    if arg in ("usdt", "доллар", "тезер"):
        await _usdt(update, args[1:], r_bids, actual_tether)
        return
    if arg in ("руб", "rub", "ruble"):
        await _rub(update, r_ask_top)
        return
    if arg in ("вона", "won", "krw"):
        await _won(update, args[1:], actual_tether)
        return
    if arg in ("йена", "jpy"):
        await _jpy(update, args[1:], actual_tether)
        return

    # Валютная пара (/курс EURUSD 100)
    await _currency_pair(update, args)


async def _all_rates(update, r_ask_top, r_bids):
    g_ask, g_bids = get_courses_from_grinex()
    tv = get_courses_from_tv()
    msg = format_all_rates_md_v2(r_ask_top, r_bids, g_ask, g_bids, tv["course"])
    await update.message.reply_text(
        msg,
        reply_markup=refresh_all_kb(),
        disable_web_page_preview=True,
        parse_mode="MarkdownV2",
    )


async def _usdt(update, extra, r_bids, actual_tether):
    if extra:
        ci = await parse_city_index(
            update,
            extra[0] if len(extra) > 0 else None,
            extra[1] if len(extra) > 1 else None,
        )
        if not ci:
            return
        course = usdt(actual_tether, ci.city, ci.index)
        msg = (
            f"💵 *Объём тезера* _({utc_now()})_\n"
            f"{course[0]} = {course[1]}\n"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    _, g_bids = get_courses_from_grinex()
    await update.message.reply_text(
        format_usdt_rub(r_bids, g_bids),
        reply_markup=refresh_simple_kb(CB.REFRESH_USDT),
        parse_mode="Markdown",
    )


async def _rub(update, r_ask_top):
    g_ask, _ = get_courses_from_grinex()
    await update.message.reply_text(
        format_rub_usdt(r_ask_top, g_ask),
        reply_markup=refresh_simple_kb(CB.REFRESH_RUB),
        parse_mode="Markdown",
    )


async def _won(update, extra, actual_tether):
    tv = get_courses_from_tv()
    tv_msg = tv["course"]
    dt = utc_from_iso(tv["time"])

    if extra:
        ci = await parse_city_index(
            update,
            extra[0] if len(extra) > 0 else None,
            extra[1] if len(extra) > 1 else None,
        )
        if not ci:
            return
        won = krw(actual_tether, ci.city, tv_msg, ci.index)
        msg = f"🇰🇷 *КУРС USDT → KRW* _({dt})_\n{won[0]} = {won[1]}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    await update.message.reply_text(
        format_won(tv_msg, dt),
        reply_markup=refresh_simple_kb(CB.REFRESH_WON),
        parse_mode="Markdown",
    )


async def _jpy(update, extra, actual_tether):
    if not extra or len(extra) != 3:
        await update.message.reply_text(
            "Ошибка при указании параметров рассчёта курса. "
            "Повторите запрос с корректным количеством параметров\n"
            "Например: `/курс йена Краснодар 145.6 1`\n",
            parse_mode="Markdown",
        )
        return

    ci = await parse_city_index(update, extra[0], extra[2])
    if not ci:
        return

    try:
        tether = float(extra[1])
    except ValueError:
        await update.message.reply_text("❌ Значение тезера должно быть числом.")
        return

    jpy_msg = jpy(actual_tether, ci.city, tether, ci.index)
    msg = (
        f"🇯🇵 *USDT → JPY* _(обновлено {utc_now()})_\n"
        f"{jpy_msg[0]} = {jpy_msg[1]}\n"
        f"*КУРС:* _{round(jpy_msg[1] * 100, 2)}_"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def _currency_pair(update, args):
    pair = parse_pair(args[0])
    if not pair:
        await update.message.reply_text(Msg.PAIR_INVALID)
        return
    base, quote = pair
    expr = " ".join(args[1:]) if len(args) > 1 else "1"

    try:
        amount = evaluate(expr)
        result = exchange.convert(base, quote, amount)
        dt = utc_from_ts(result["timestamp"])
        await update.message.reply_text(
            format_pair(base, quote, amount, result["converted"], result["rate"], dt),
            reply_markup=refresh_pair_kb(f"{base}{quote}", amount),
            disable_web_page_preview=True,
        )
    except Exception as e:
        await update.message.reply_text(f"⚠ Ошибка при получении курса: {e}")


# ============== /<EURUSD> [amount] ==============

async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lstrip("/")
    parts = text.split(maxsplit=1)
    pair = parse_pair(parts[0])
    if not pair:
        await update.message.reply_text(Msg.PAIR_INVALID)
        return

    base, quote = pair
    expr = parts[1] if len(parts) > 1 else "1"

    try:
        amount = evaluate(expr)
    except Exception as e:
        await update.message.reply_text(f"Ошибка в выражении суммы: {e}")
        return

    try:
        result = exchange.convert(base, quote, amount)
        dt = utc_from_ts(result["timestamp"])
        await update.message.reply_text(
            format_pair(base, quote, amount, result["converted"], result["rate"], dt),
            reply_markup=refresh_pair_kb(f"{base}{quote}", amount),
            disable_web_page_preview=True,
        )
    except Exception as e:
        await update.message.reply_text(f"⚠ Ошибка при получении курса: {e}")