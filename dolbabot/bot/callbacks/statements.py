from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from db.handlers.model_handlers import (
    transaction_handler, transaction_history_handler,
)
from dto.transaction import TransactionDTO
from services.excel_worker import create_dataframe_from_object, create_temp_excel_file
from utils.logger import logger

from ..constants import CB, Msg
from ..decorators import safe_callback


@safe_callback(Msg.STATEMENT_ERROR)
async def create_bank_statement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    logger.info(f"[DATA]: {q.data}")

    chat_id = q.message.chat.id

    if q.data == CB.STATEMENT_CURRENT:
        transactions = transaction_handler.get_all_with_joins(
            filters={"is_checked": False, "group.id": chat_id},
        )
        statement_type = "Текущая"
    elif q.data == CB.STATEMENT_FULL:
        transactions = transaction_handler.get_all_with_joins(
            filters={"group.id": chat_id},
        )
        history = transaction_history_handler.get_all_with_joins(
            filters={"group.id": chat_id},
        )
        transactions += TransactionDTO.from_history(history)
        statement_type = "Полная"
    else:
        return

    if not transactions:
        await q.message.reply_text(Msg.STATEMENT_EMPTY)
        return

    transactions.sort(key=lambda t: t.created_at, reverse=True)

    df = create_dataframe_from_object(transactions)
    bytes_io = create_temp_excel_file(df)
    date = datetime.now().strftime("%d_%m_%Y")
    await q.message.reply_document(
        document=bytes_io,
        filename=f"{statement_type}_выписка_на_{date}_{chat_id}.xlsx",
    )