from telegram.ext import Application
from bot import register_handlers
from config import config
from datetime import datetime
from utils.logger import logger

def main():
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    register_handlers(app)
    logger.info("Бот запущен... " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    app.run_polling()


if __name__ == "__main__":
    main()
