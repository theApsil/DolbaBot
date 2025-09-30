from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime
from exchanges.base import CurrencyLayerExchange
from utils.calculator import Calculator

HELP_TEXT = """
Доступные команды:
 - /start — start bot
 - /help — list commands
 - /kurs <pair> <amount> — currency rate (example: /kurs eurusd 100)
 - /eurusd <amount or formula> — alternative input (example: /eurusd 50+25%)
 - /(expression) — calculator (example: /(2+3)*100-50%)
"""

exchange = CurrencyLayerExchange()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("```"
                                    "🤖 Бот запущен."
                                    "```", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)

# /eurusd 100 или /usdrub 500 или /<expr>
async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.lstrip("/")
    parts = cmd.split(maxsplit=1)

    pair = parts[0].upper()
    expr = parts[1] if len(parts) > 1 else "1"

    try:
        amount = Calculator.evaluate(expr)

        result = exchange.convert(pair[:3], pair[3:], amount)
        dt = datetime.utcfromtimestamp(result['timestamp']).strftime("%d.%m %H:%M UTC")

        msg = (
            f"{result['converted']:.3f} {pair[3:]} = ({amount}) {pair[:3]}\n"
            f"1 {pair[:3]} = {result['rate']:.5f} {pair[3:]}\n"
            f"at {dt} currencylayer.com"
        )

        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{pair}_{amount}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    except Exception as e:
        msg = f"⚠ Error: {e}"
        reply_markup = None

    await update.message.reply_text(
        msg,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Укажите валютную пару. Пример: /курс eurusd 100")
        return

    pair = args[0].upper()
    amount = float(args[1]) if len(args) > 1 else 1.0
    base, quote = pair[:3], pair[3:]

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
        result = Calculator.evaluate(expr)
        msg = f"{expr} = {result}"
    except Exception as e:
        msg = f"⚠ Error: {e}"

    await update.message.reply_text(msg)