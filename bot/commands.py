import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from exchanges.base import CurrencyLayerExchange
from exchanges.grinex import get_courses_from_grinex, normalize_grinex_data
from exchanges.rapira import get_courses_from_rapira, normalize_rapira_data
from exchanges.traidingview import get_courses_from_tv
from utils.calculator import evaluate

exchange = CurrencyLayerExchange()

HELP_TEXT = """
Доступные команды:
 - /старт — запустить бота
 - /помоги — список команд
 - /курс <пара_валют> <размер или выражение> — курс валют (/курс eurusd 100)
 - /курс — выдает все курсы: rub/usdt, usdt/rub, usdt/won
 - /курс руб — стакан RUB→USDT
 - /курс usdt — курс USDT→RUB
 - /курс вона — курс USDT→KRW
 - /(выражение) — калькулятор
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("```🤖 Бот запущен.```", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


# === /курс ===
async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()
    args = text[1:]

    if not args:
        r_ask, r_bids = get_courses_from_rapira()
        g_ask, g_bids = get_courses_from_grinex()
        tv_msg = get_courses_from_tv()

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask)+ f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 КУРСЫ (обновлено {dt})\n\n"
            f"\bRAPIRA\b - https://rapira.net/exchange/USDT_RUB\n{rapira_msg}\n\n"
            f"\bGRINEX\b - https://grinex.io/trading/usdta7a5\n{grinex_msg}\n\n"
            f"\bTRADINGVIEW\b - https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW\n🇰🇷KRW/USDT - {tv_msg}"
        )

        keyboard = [[InlineKeyboardButton("🔄 Обновить всё", callback_data="refresh_all")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard),
                                        disable_web_page_preview=True)
        return

    arg = args[0].lower()

    # === /курс usdt ===
    if arg in ["usdt", "доллар", "тезер"]:
        r_ask, r_bids = get_courses_from_rapira()
        g_ask, g_bids = get_courses_from_grinex()
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        msg = (
            f"💵 КУРС USDT → RUB (обновлено {dt})\n\n"
            f"RAPIRA\n🇺🇸USDT/RUB: {r_bids}\n\n"
            f"GRINEX\n🇺🇸USDT/RUB: {g_bids}"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_usdt")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        return

    # === /курс руб ===
    if arg in ["руб", "rub", "ruble"]:
        r_ask, _ = get_courses_from_rapira()
        g_ask, _ = get_courses_from_grinex()
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        msg = (
            f"💱 СТАКАН RUB → USDT (обновлено {dt})\n\n"
            f"RAPIRA\n{normalize_rapira_data(r_ask)}\n\n"
            f"GRINEX\n{normalize_grinex_data(g_ask)}"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_rub")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        return

    # === /курс вона ===
    if arg in ["вона", "won", "krw"]:
        tv_msg = get_courses_from_tv()
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        msg = f"🇰🇷 КУРС USDT → KRW (обновлено {dt})\n\n{tv_msg}"
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_won")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        return

    # === Валютная пара ===
    raw_pair = re.sub(r'[^A-Za-z]', '', arg).upper()
    if len(raw_pair) < 6:
        await update.message.reply_text("❌ Неверная пара. Пример: EURUSD")
        return

    base, quote = raw_pair[:3], raw_pair[3:6]
    expr = " ".join(args[1:]) if len(args) > 1 else "1"

    try:
        amount = evaluate(expr)
        result = exchange.convert(base, quote, amount)
        dt = datetime.utcfromtimestamp(result["timestamp"]).strftime("%d.%m %H:%M UTC")
        msg = (
            f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
            f"1 {base} = {result['rate']:.5f} {quote}\n"
            f"at {dt} currencylayer.com"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить курс", callback_data=f"refresh_{base}{quote}_{amount}")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"⚠ Ошибка при получении курса: {e}")


# TODO: INLINE Refresh
async def kurs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # === Refresh all ===
    if data == "refresh_all":
        r_ask, r_bids = get_courses_from_rapira()
        g_ask, g_bids = get_courses_from_grinex()
        tv_msg = get_courses_from_tv()

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask)+ f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 КУРСЫ (обновлено {dt})\n\n"
            f"*RAPIRA* - https://rapira.net/exchange/USDT_RUB\n{rapira_msg}\n\n"
            f"*GRINEX* - https://grinex.io/trading/usdta7a5\n{grinex_msg}\n\n"
            f"*TRADINGVIEW* - https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW\n🇰🇷KRW/USDT - {tv_msg}"
        )

        kb = [[InlineKeyboardButton("🔄 Обновить всё", callback_data="refresh_all")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), disable_web_page_preview=True)
        return

    # === Refresh rub/usdt/usdt/krw ===
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
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            await query.edit_message_text(f"⚠ Ошибка при обновлении курса: {e}")


async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lstrip("/")
    parts = text.split(maxsplit=1)
    raw_pair = parts[0]
    pair_clean = re.sub(r'[^A-Za-z]', '', raw_pair).upper()
    if len(pair_clean) < 6:
        await update.message.reply_text("❌ Неверная пара. Пример: /eurusd 100")
        return
    base, quote = pair_clean[:3], pair_clean[3:6]

    expr = parts[1] if len(parts) > 1 else "1"
    try:
        amount = evaluate(expr)
    except Exception as e:
        await update.message.reply_text(f"Ошибка в выражении суммы: {e}")
        return

    try:
        result = exchange.convert(base, quote, amount)
        dt = datetime.utcfromtimestamp(result['timestamp']).strftime("%d.%m %H:%M UTC")

        msg = (
            f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
            f"1 {base} = {result['rate']:.5f} {quote}\n"
            f"at {dt} currencylayer.com"
        )

        keyboard = [
            [InlineKeyboardButton("🔄 Обновить курс", callback_data=f"refresh_{base}{quote}_{amount}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    except Exception as e:
        msg = f"⚠ Ошибка при получении курса: {e}"
        reply_markup = None

    await update.message.reply_text(
        msg,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = update.message.text.lstrip("/")
    try:
        result = evaluate(expr)
        await update.message.reply_text(f"{expr} = {result}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")