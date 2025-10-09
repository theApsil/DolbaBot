from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler

from exchanges.grinex import get_courses_from_grinex, normalize_grinex_data
from exchanges.rapira import get_courses_from_rapira, normalize_rapira_data
from exchanges.traidingview import get_courses_from_tv
from .commands import help_command , kurs_command, pair_command, start_command, calc_command
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from exchanges.base import CurrencyLayerExchange
from datetime import datetime
import re


exchange = CurrencyLayerExchange()


async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    r_ask, r_bids = get_courses_from_rapira()
    g_ask, g_bids = get_courses_from_grinex()


    # === Refresh all ===
    if data == "refresh_all":
        tv_msg = get_courses_from_tv()

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask) + f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 КУРСЫ (обновлено {dt})\n\n"
            f"*RAPIRA2 - https://rapira.net/exchange/USDT_RUB\n{rapira_msg}\n\n"
            f"*GRINEX2 - https://grinex.io/trading/usdta7a5\n{grinex_msg}\n\n"
            f"*TRADINGVIEW2 - https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW\n🇰🇷KRW/USDT - {tv_msg}"
        )

        kb = [[InlineKeyboardButton("🔄 Обновить всё", callback_data="refresh_all")]]
        reply_markup = InlineKeyboardMarkup(kb)
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), disable_web_page_preview=True)
        return

    # TODO: Refresh rub/usdt/usdt/krw ===
    elif data in ["refresh_rub", "refresh_usdt", "refresh_won"]:
        fake_update = type("obj", (object,), {"message": query.message})
        fake_context = type("obj", (object,), {"args": [data.split("_")[1]]})
        await kurs_command(fake_update, fake_context)
        return

    # === Refresh pair ===
    else:
        try:
            _, pair, amount = data.split("_")
            base, quote = pair[:3], pair[3:]
            amount = float(amount)
            result = exchange.convert(base, quote, amount)
            dt = datetime.utcfromtimestamp(result["timestamp"]).strftime("%d.%m %H:%M UTC")
            msg = (
                f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
                f"1 {base} = {result['rate']:.5f} {quote}\n"
                f"at {dt} currencylayer.com"
            )
            kb = [[InlineKeyboardButton("🔄 Обновить курс", callback_data=f"refresh_{base}{quote}_{amount}")]]
            reply_markup = InlineKeyboardMarkup(kb)
            await query.message.reply_text(
                msg,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as e:
            await query.edit_message_text(f"⚠ Ошибка при обновлении курса: {e}")

    await query.message.reply_text(
        msg,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

def register_handlers(app):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs_command))

    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(старт|start)\b", re.IGNORECASE)), start_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(помоги|help)\b", re.IGNORECASE)), help_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(курс|kurs)\b", re.IGNORECASE)), kurs_command))

    app.add_handler(CallbackQueryHandler(refresh_callback, pattern=r"^refresh_"))
    app.add_handler(MessageHandler(filters.Regex(r"^/[^a-zA-Z]"), calc_command))
    # любые команды, включая русские (/курс, /евро)
    app.add_handler(MessageHandler(filters.COMMAND, pair_command))
