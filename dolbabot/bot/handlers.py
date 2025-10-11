from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import re

from exchanges.grinex import get_courses_from_grinex, normalize_grinex_data
from exchanges.rapira import get_courses_from_rapira, normalize_rapira_data
from exchanges.traidingview import get_courses_from_tv
from exchanges.base import CurrencyLayerExchange
from .commands import help_command, kurs_command, pair_command, start_command, calc_command

exchange = CurrencyLayerExchange()


# === Обработка всех Inline-кнопок ===
async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
    r_ask, r_bids = get_courses_from_rapira()
    g_ask, g_bids = get_courses_from_grinex()

    r_ask = r_ask[5:10]
    # === 1. Обновление всех курсов ===
    if data == "refresh_all":
        tv_req = get_courses_from_tv()
        tv_msg = tv_req["course"]

        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask) + f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 *КУРСЫ* _(обновлено {dt})_\n\n"
            f"*RAPIRA* — [ссылка](https://rapira.net/exchange/USDT_RUB)\n{rapira_msg}\n\n"
            f"*GRINEX* — [ссылка](https://grinex.io/trading/usdta7a5)\n{grinex_msg}\n\n"
            f"*TRADINGVIEW* — [ссылка](https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW)\n🇰🇷KRW/USDT — {tv_msg}"
        )

        await query.message.reply_text(msg,
                                      parse_mode="Markdown",
                                       disable_web_page_preview=True
                                       )
        return

    # === 2. Обновление RUB / USDT / WON ===
    if data in ["refresh_usdt", "refresh_rub", "refresh_won"]:
        arg = data.split("_")[1]

        if arg == "usdt":
            msg = (
                f"💵 *КУРС USDT → RUB* _(обновлено {dt})_\n\n"
                f"*RAPIRA*\n🇺🇸USDT/RUB: {r_bids}\n\n"
                f"*GRINEX*\n🇺🇸USDT/RUB: {g_bids}"
            )
        elif arg == "rub":
            msg = (
                f"💱 *СТАКАН RUB → USDT* _(обновлено {dt})_\n\n"
                f"*RAPIRA*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_rapira_data(r_ask)}\n\n"
                f"*GRINEX*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_grinex_data(g_ask)}\n\n"
            )
        else:  # won
            tv_req = get_courses_from_tv()
            tv_msg = tv_req["course"]
            tv_time = datetime.fromisoformat(tv_req["time"]).strftime("%d.%m %H:%M UTC")

            msg = f"🇰🇷 *КУРС USDT → KRW* _(обновлено {tv_time})_\n{tv_msg}"

        await query.message.reply_text(msg,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return

    # === 3. Обновление валютной пары (EURUSD и т.д.) ===
    if data.startswith("refresh_") and len(data.split("_")) == 3:
        try:
            _, pair, amount = data.split("_")
            base, quote = pair[:3], pair[3:]
            amount = float(amount)
            result = exchange.convert(base, quote, amount)
            msg = (
                f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
                f"1 {base} = {result['rate']:.5f} {quote}\n"
                f"_(обновлено {dt})_ через currencylayer.com"
            )
            await query.message.reply_text(msg,
                                            parse_mode="Markdown",
                                            disable_web_page_preview=True)
        except Exception as e:
            await query.message.reply_text(f"⚠ Ошибка при обновлении курса: {e}")
        return


# === Регистрация всех хэндлеров ===
def register_handlers(app):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs_command))

    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(старт|start)\b", re.IGNORECASE)), start_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(помоги|help)\b", re.IGNORECASE)), help_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(курс|kurs)\b", re.IGNORECASE)), kurs_command))

    app.add_handler(CallbackQueryHandler(refresh_callback, pattern=r"^refresh_"))
    app.add_handler(MessageHandler(filters.Regex(r"^/[^a-zA-Z]"), calc_command))
    app.add_handler(MessageHandler(filters.COMMAND, pair_command))
