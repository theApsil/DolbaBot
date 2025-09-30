from telegram import Update
from telegram.ext import ContextTypes
from exchanges.base import XEExchange

HELP_TEXT = '''
Доступные команды:
/помоги — список команд
/курс <пара> <сумма> — курс валюты (пример: /курс eurusd 100)
/eurusd <сумма> — альтернативная запись (пример: /eurusd 50)

'''

xe = XEExchange()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)

async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Укажите валютную пару. Пример: /курс eurusd 100")
        return

    pair = args[0].upper()
    amount = float(args[1]) if len(args) > 1 else 1.0

    base, quote = pair[:3], pair[3:]

    try:
        result = xe.convert(base, quote, amount)
        msg = (
            f"{amount} {base} = {result['converted']:.4f} {quote}\n"
            f"1 {base} = {result['rate']:.5f} {quote}\n"
            f"Источник: XE.com"
        )
    except Exception as e:
        msg = f"⚠ Ошибка при получении курса: {e}"

    await update.message.reply_text(msg)


# /eurusd 100 или /usdrub 500
async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.lstrip("/")
    parts = cmd.split()

    pair = parts[0].upper()
    amount = float(parts[1]) if len(parts) > 1 else 1.0
    base, quote = pair[:3], pair[3:]

    try:
        result = xe.convert(base, quote, amount)
        msg = (
            f"{amount} {base} = {result['converted']:.4f} {quote}\n"
            f"1 {base} = {result['rate']:.5f} {quote}\n"
            f"Источник: XE.com"
        )
    except Exception as e:
        msg = f"⚠ Ошибка при получении курса: {e}"

    await update.message.reply_text(msg)