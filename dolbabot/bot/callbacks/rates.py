from telegram import Update
from telegram.ext import ContextTypes

from exchanges.base import CurrencyLayerExchange
from exchanges.grinex import get_courses_from_grinex
from exchanges.rapira import get_courses_from_rapira
from exchanges.traidingview import get_courses_from_tv

from ..constants import CB
from ..decorators import safe_callback
from ..formatters import (
    format_all_rates, format_usdt_rub, format_rub_usdt,
    format_won, format_pair, utc_from_iso,
)
from ..keyboards import refresh_all_kb, refresh_simple_kb, refresh_pair_kb


exchange = CurrencyLayerExchange()


@safe_callback()
async def refresh_all_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    r_ask, r_bids = get_courses_from_rapira()
    g_ask, g_bids = get_courses_from_grinex()
    tv = get_courses_from_tv()

    msg = format_all_rates(r_ask[5:10], r_bids, g_ask, g_bids, tv["course"])
    await q.message.reply_text(
        msg, reply_markup=refresh_all_kb(),
        parse_mode="Markdown", disable_web_page_preview=True,
    )


@safe_callback()
async def refresh_usdt_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, r_bids = get_courses_from_rapira()
    _, g_bids = get_courses_from_grinex()
    await q.message.reply_text(
        format_usdt_rub(r_bids, g_bids),
        reply_markup=refresh_simple_kb(CB.REFRESH_USDT),
        parse_mode="Markdown", disable_web_page_preview=True,
    )


@safe_callback()
async def refresh_rub_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    r_ask, _ = get_courses_from_rapira()
    g_ask, _ = get_courses_from_grinex()
    await q.message.reply_text(
        format_rub_usdt(r_ask[5:10], g_ask),
        reply_markup=refresh_simple_kb(CB.REFRESH_RUB),
        parse_mode="Markdown", disable_web_page_preview=True,
    )


@safe_callback()
async def refresh_won_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    tv = get_courses_from_tv()
    await q.message.reply_text(
        format_won(tv["course"], utc_from_iso(tv["time"])),
        reply_markup=refresh_simple_kb(CB.REFRESH_WON),
        parse_mode="Markdown", disable_web_page_preview=True,
    )


@safe_callback("⚠️ Ошибка при обновлении курса.")
async def refresh_pair_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    _, pair, amount_str = q.data.split("_")
    base, quote = pair[:3].upper(), pair[3:].upper()
    amount = float(amount_str)

    result = exchange.convert(base, quote, amount)
    msg = format_pair(base, quote, amount, result["converted"], result["rate"])
    await q.message.reply_text(
        msg, reply_markup=refresh_pair_kb(pair, amount),
        parse_mode="Markdown", disable_web_page_preview=True,
    )