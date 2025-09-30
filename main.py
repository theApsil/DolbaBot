from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.commands import help_command, kurs_command, pair_command, start_command
from bot.handlers import refresh_callback
from config import TELEGRAM_TOKEN


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # основные команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs_command))

    # кнопка обновления курса
    app.add_handler(CallbackQueryHandler(refresh_callback, pattern=r"^refresh_"))

    # все неизвестные команды (в том числе валютные пары)
    app.add_handler(MessageHandler(filters.COMMAND, pair_command))

    app.run_polling()


if __name__ == "__main__":
    main()
