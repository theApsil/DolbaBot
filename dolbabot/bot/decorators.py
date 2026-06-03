from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import logger
from .constants import Msg


def safe_handler(error_text: str = Msg.GENERIC_ERROR):
    """Для MessageHandler: логирует исключения и шлёт сообщение в чат."""
    def deco(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                return await func(update, context)
            except Exception as e:
                logger.exception(f"Error in handler {func.__name__}: {e}")
                if update.message:
                    await update.message.reply_text(error_text)
        return wrapper
    return deco


def safe_callback(error_text: str = Msg.GENERIC_ERROR):
    """Для CallbackQueryHandler: ловит исключения, шлёт сообщение пользователю."""
    def deco(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                return await func(update, context)
            except Exception as e:
                logger.exception(f"Error in callback {func.__name__}: {e}")
                if update.callback_query:
                    try:
                        await update.callback_query.edit_message_text(error_text)
                    except Exception:
                        await update.callback_query.message.reply_text(error_text)
        return wrapper
    return deco


def admin_only(func):
    """Проверяет is_admin из context.user_data['user']."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = context.user_data.get("user") or {}
        if not user.get("is_admin"):
            await update.message.reply_text(Msg.NO_ACCESS)
            return
        return await func(update, context)
    return wrapper