import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from exchanges.base import CurrencyLayerExchange
from exchanges.grinex import get_courses_from_grinex, normalize_grinex_data
from exchanges.rapira import get_courses_from_rapira, normalize_rapira_data
from exchanges.traidingview import get_courses_from_tv
from utils.calculator import evaluate
from utils.helpers import escape_md
from services.formulas import usdt, krw, jpy
from utils.rapira_decision import make_decision
from utils.logger import logger

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

    r_ask, r_bids = get_courses_from_rapira()
    actual_tether = make_decision(r_ask)['price']
    logger.info(F"DECISION RAPIRA: {actual_tether}")
    r_ask = r_ask[5:10]
    if not args:
        g_ask, g_bids = get_courses_from_grinex()
        tv_req = get_courses_from_tv()
        tv_msg = tv_req["course"]

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask)+ f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 *КУРСЫ* \({escape_md(dt)}\)\n\n"
            f"*RAPIRA* — [ссылка]({escape_md('https://rapira.net/exchange/USDT_RUB')})\n{escape_md(rapira_msg)}\n\n"
            f"*GRINEX* — [ссылка]({escape_md('https://grinex.io/trading/usdta7a5')})\n{escape_md(grinex_msg)}\n\n"
            f"*TRADINGVIEW* — [ссылка]({escape_md('https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW')})\n🇰🇷KRW/USDT — {escape_md(tv_msg)}"
        )

        keyboard = [[InlineKeyboardButton("🔄 Обновить всё", callback_data="refresh_all")]]
        await update.message.reply_text(msg,
                                        reply_markup=InlineKeyboardMarkup(keyboard),
                                        disable_web_page_preview=True, parse_mode="MarkdownV2")
        return

    arg = args[0].lower()

    # === /курс usdt ===
    if arg in ["usdt", "доллар", "тезер"]:
        new_args = args[1:]
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")

        if new_args:
            city, index = new_args[0], new_args[1]
            city = city.title()

            # TODO: Нормализация сопоставления городов и их индекса
            course = usdt(actual_tether, city, float(index))

            msg = (
                f"💵 *Объём тезера* _({dt})_\n"
                f"{course[0]} = {course[1]}\n"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        g_ask, g_bids = get_courses_from_grinex()
        msg = (
            f"💵 *КУРС USDT → RUB* _({dt})_\n\n"
            f"*RAPIRA*\n🇺🇸USDT/RUB: {r_bids}\n\n"
            f"*GRINEX*\n🇺🇸USDT/RUB: {g_bids}"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_usdt")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    # === /курс руб ===
    if arg in ["руб", "rub", "ruble"]:
        g_ask, _ = get_courses_from_grinex()
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        msg = (
            f"💱 *СТАКАН RUB → USDT* _({dt})_\n\n"
            f"*RAPIRA*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_rapira_data(r_ask)}\n\n"
            f"*GRINEX*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_grinex_data(g_ask)}\n\n"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_rub")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    # === /курс вона ===
    if arg in ["вона", "won", "krw"]:
        tv_req = get_courses_from_tv()
        tv_msg = tv_req["course"]
        dt = datetime.fromisoformat(tv_req["time"]).strftime("%d.%m %H:%M UTC")
        new_args = args[1:]

        if new_args:
            city, index = new_args[0], new_args[1]
            city = city.title()
            # TODO: Нормализация сопоставления городов и их индекса
            won = krw(actual_tether, city, tv_msg, float(index))
            msg = (
                f"🇰🇷 *КУРС USDT → KRW* _({dt})_\n"
                f"{won[0]} = {won[1]}\n"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        msg = f"🇰🇷 *КУРС USDT → KRW* _({dt})_\n{tv_msg}"
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_won")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if arg in ["йена", "jpy"]:
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        new_args = args[1:]
        if not new_args or len(new_args) != 3:
            msg = (
                f"Ошибка при указании параметров рассчёта курса. Повторите запрос с корректным количеством параметров\n"
                f"Например: `/курс йена Краснодар 145.6 1`\n"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return
        else:
            city, tether, index = new_args[0], float(new_args[1]), float(new_args[2])
            city = city.title()
            # TODO: Нормализация сопоставления городов и их индекса

            jpy_msg = jpy(actual_tether, city, tether, index)
            msg = (
                f"🇯🇵 *USDT → JPY* _(обновлено {dt})_\n"
                f"{jpy_msg[0]} = {jpy_msg[1]}\n"
                f"*КУРС:* _{round(jpy_msg[1] * 100, 2)}_"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
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