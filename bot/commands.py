from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime
from exchanges.base import CurrencyLayerExchange

from utils.calculator import evaluate
import re

HELP_TEXT = """
Доступные команды:
 - /start - запустить бота
 - /help - список команд
 - /kurs <pair> <amount> - курс валют (/kurs eurusd 100)
 - /eurusd <amount or formula> - альтернативный курс валют (/eurusd 50+25%)
 - /(expression) — калькулятор (доступен и в команде вычисления курса) (/(2+3)*100-50%)
"""

exchange = CurrencyLayerExchange()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("```"
                                    "🤖 Бот запущен."
                                    "```", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)

# /eurusd 100 или /usdrub 500 или /<expr>
# /eurusd 100 или /usdrub 500 или /<expr>
async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if context.args and len(context.args) > 0:
        args = context.args
    else:
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            args = parts[1].split()
        else:
            args = []

    if not args:
        # === пустая команда /курс → выводим все курсы ===
        def safe_call(fn, name):
            try:
                return fn()
            except Exception as e:
                return f"⚠ {name}: ошибка ({e})"

        rapira_msg = safe_call(get_rub_usdt_rapira(), "Rapira")
        grinex_msg = safe_call(get_rub_usdt_grinex(), "Grinex")
        tv_msg = safe_call(get_usdt_won_tradingview(), "TradingView")

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")

        msg = (
            f"📊 КУРСЫ (обновлено {dt})\n\n"
            f"RAPIRA\n{rapira_msg}\n\n"
            f"GRINEX\n{grinex_msg}\n\n"
            f"TRADINGVIEW\n{tv_msg}"
        )

        keyboard = [[InlineKeyboardButton("🔄 Обновить все", callback_data="refresh_all")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            msg,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        return

    # === обычный режим (пара+сумма) ===
    raw_pair = args[0]
    pair_clean = re.sub(r'[^A-Za-z]', '', raw_pair).upper()
    if len(pair_clean) < 6:
        await update.message.reply_text("❌ Неверная пара. Пример: EURUSD")
        return

    base, quote = pair_clean[:3], pair_clean[3:6]

    expr = " ".join(args[1:]) if len(args) > 1 else "1"
    try:
        amount = evaluate(expr)
    except Exception as e:
        await update.message.reply_text(f"Ошибка в выражении суммы: {e}")
        return

    try:
        result = exchange.convert(base, quote, amount)
        dt = datetime.utcfromtimestamp(result["timestamp"]).strftime("%d.%m %H:%M UTC")

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
        disable_web_page_preview=True,
    )


async def kurs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # === обновление всех курсов ===
    if data == "refresh_all":
        def safe_call(fn, name):
            try:
                return fn()
            except Exception as e:
                return f"⚠ {name}: ошибка ({e})"

        rapira_msg = safe_call(get_rub_usdt_rapira, "Rapira")
        grinex_msg = safe_call(get_rub_usdt_grinex, "Grinex")
        tv_msg = safe_call(get_usdt_won_tradingview, "TradingView")

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")

        msg = (
            f"📊 КУРСЫ (обновлено {dt})\n\n"
            f"RAPIRA\n{rapira_msg}\n\n"
            f"GRINEX\n{grinex_msg}\n\n"
            f"TRADINGVIEW\n{tv_msg}"
        )

        keyboard = [[InlineKeyboardButton("🔄 Обновить все", callback_data="refresh_all")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(msg, reply_markup=reply_markup, disable_web_page_preview=True)


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