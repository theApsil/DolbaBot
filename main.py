from telegram.ext import Application
from bot.handlers import register_handlers
from config import TELEGRAM_TOKEN


def main():
    print(TELEGRAM_TOKEN)

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)

    print("🤖 DolbaBot запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
