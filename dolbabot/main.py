from telegram.ext import Application
from bot import register_handlers
from config import TELEGRAM_TOKEN
from datetime import datetime


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)
    print("Бот запущен...", datetime.now())
    app.run_polling()


if __name__ == "__main__":
    main()
