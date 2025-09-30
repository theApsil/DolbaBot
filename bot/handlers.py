from telegram.ext import CommandHandler, MessageHandler, filters
from .commands import help_command #, kurs_command, pair_command


def register_handlers(app):
    app.add_handler(CommandHandler("help", help_command))

