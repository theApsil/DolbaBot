from telegram import Update
from telegram.ext import ContextTypes

from utils.calculator import evaluate

from ..constants import HELP_TEXT, Msg
from ..parsers import PAIR_RE


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("```🤖 Бот запущен.```", parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = update.message.text.lstrip("/")
    try:
        result = evaluate(expr)
        await update.message.reply_text(f"{expr} = {result}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def error_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(Msg.UNKNOWN_COMMAND)


async def slash_dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Диспетчер для /<token>:
      - /EURUSD (6 букв, без аргументов) → курс пары
      - /<account> <expr>                → пополнение счёта
    """
    from .rates import pair_command            # отложенный импорт — нет циклов
    from .accounts import add_money_command

    text = update.message.text.strip()
    parts = text.split(maxsplit=1)
    command = parts[0].lstrip("/")
    has_args = len(parts) > 1

    if PAIR_RE.match(command) and not has_args:
        await pair_command(update, context)
        return

    await add_money_command(update, context)