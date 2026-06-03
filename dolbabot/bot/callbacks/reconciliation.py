from telegram import Update
from telegram.ext import ContextTypes

from services.accounts import reconcile_group
from utils.logger import logger

from ..constants import CB, Msg
from ..decorators import safe_callback


@safe_callback(Msg.RECONCILE_ERROR)
async def reconciliation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == CB.RECONCILE_CANCEL:
        await q.edit_message_text(Msg.RECONCILE_CANCELED)
        return

    if q.data == CB.RECONCILE_CONFIRM:
        logger.info(f"[GROUP]: {q.message.chat.id}")
        count = reconcile_group(q.message.chat.id)
        await q.edit_message_text(f"✅ Балансы сверены. ({count} транзакций отмечено)")