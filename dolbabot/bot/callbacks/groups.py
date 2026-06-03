from telegram import Update
from telegram.ext import ContextTypes

from db.handlers.model_handlers import telegram_group_handler
from utils.logger import logger

from ..constants import CB, Msg
from ..decorators import safe_callback


@safe_callback(Msg.TAG_CHANGE_ERROR)
async def change_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    logger.info(f"[DATA]: {q.data}")

    if q.data == CB.GROUP_TAG_CANCEL:
        await q.edit_message_text(Msg.TAG_CHANGE_CANCELED)
        return

    if q.data != CB.GROUP_TAG_CONFIRM:
        return

    stored = context.user_data.get(f"data_for_{q.message.message_id}")
    if not stored:
        await q.message.reply_text(Msg.TAG_CHANGE_FOREIGN)
        return

    new_group = telegram_group_handler.update(
        filters={"id": stored["group_id"]},
        updates={"group_tag": str(stored["new_tag"])},
    )
    await q.edit_message_text(
        f"✅ Тег группы *{new_group.name}* изменён.\n"
        f"`Новый тег: {stored['new_tag']}`",
        parse_mode="Markdown",
    )