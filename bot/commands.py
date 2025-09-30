from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = '''
Доступные команды:
/помоги — список команд
/курс <пара> <сумма> — курс валюты (пример: /курс eurusd 100)
/eurusd <сумма> — альтернативная запись (пример: /eurusd 50)

лялялляя я Семён Лобанов
'''

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)