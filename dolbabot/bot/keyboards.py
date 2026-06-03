from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .constants import CB

def refresh_all_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Обновить всё", callback_data=CB.REFRESH_ALL)]])

def refresh_simple_kb(callback_data: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Обновить", callback_data=callback_data)]])

def refresh_pair_kb(pair: str, amount: float):
    cb = CB.REFRESH_PAIR.format(pair=pair, amount=amount)
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Обновить курс", callback_data=cb)]])

def cancel_tx_kb(tx_id):
    cb = CB.CANCEL_TX.format(tx_id=tx_id)
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отменить", callback_data=cb)]])

def statement_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📄 Текущая выписка", callback_data=CB.STATEMENT_CURRENT),
        InlineKeyboardButton("📜 Полная выписка", callback_data=CB.STATEMENT_FULL),
    ]])

def reconcile_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Сверено✅", callback_data=CB.RECONCILE_CONFIRM),
        InlineKeyboardButton("Отменить❌", callback_data=CB.RECONCILE_CANCEL),
    ]])

def delete_account_kb(account_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Удалить", callback_data=CB.ACCOUNT_DELETE_CONFIRM.format(id=account_id)),
        InlineKeyboardButton("❌ Отмена", callback_data=CB.ACCOUNT_DELETE_CANCEL),
    ]])

def group_tag_kb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Изменить", callback_data=CB.GROUP_TAG_CONFIRM),
        InlineKeyboardButton("❌ Отмена", callback_data=CB.GROUP_TAG_CANCEL),
    ]])