from telegram import Update
from telegram.ext import ContextTypes

from db.handlers.model_handlers import bank_account_handler, telegram_user_handler
from utils.logger import logger

from services.accounts import (
    cancel_transaction, TxNotFound, TxAlreadyChecked, TxAccountMissing,
)

from ..constants import CB, Msg
from ..decorators import safe_callback
from ..formatters import format_tx_cancel


@safe_callback(Msg.TX_CANCEL_ERROR)
async def cancel_transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    tx_id = q.data.split("_", 1)[1]
    logger.info(f"[transaction_id]: {tx_id}")

    try:
        result = cancel_transaction(tx_id)
    except TxNotFound:
        await q.edit_message_text(Msg.TX_NOT_FOUND)
        return
    except TxAlreadyChecked:
        await q.edit_message_text(Msg.TX_ALREADY_CHECKED)
        return
    except TxAccountMissing:
        await q.edit_message_text(Msg.TX_ACC_MISSING)
        return

    user_by = telegram_user_handler.get_one(id=q.from_user.id)
    msg = format_tx_cancel(
        amount=result.amount,
        decimals=result.decimals,
        new_balance=result.new_balance,
        account_name=result.account_name,
        user_tag=user_by.telegram_tag,
    )
    await q.edit_message_text(msg, parse_mode="HTML", reply_markup=None)
    await q.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)


@safe_callback("⚠️ Произошла ошибка при удалении счёта.")
async def delete_account_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    logger.info(f"[DATA]: {q.data}")

    if q.data == CB.ACC_DELETE_CANCEL:
        await q.edit_message_text(Msg.ACC_DELETE_CANCELED)
        return

    account_id = q.data.rsplit("_", 1)[-1]
    account = bank_account_handler.get_one(id=account_id)
    if not account:
        await q.edit_message_text(Msg.ACC_ALREADY_DELETED)
        return

    if not bank_account_handler.delete(id=account_id):
        await q.edit_message_text(Msg.ACC_DELETE_FAILED)
        return

    await q.edit_message_text(
        f"🗑 Счёт *{account.account_name.upper()}* и все связанные данные удалены.",
        parse_mode="Markdown",
    )