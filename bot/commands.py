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
async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Укажите валютную пару. Пример: /курс eurusd 100")
        return

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