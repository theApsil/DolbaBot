from telegram.ext import CommandHandler, MessageHandler, filters
from .commands import help_command , kurs_command, pair_command


def register_handlers(app):
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs_command))
    # команды вида /eurusd, /usdrub, /btcusdt
    app.add_handler(MessageHandler(filters.COMMAND, pair_command))

