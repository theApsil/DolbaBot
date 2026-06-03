from telegram import Update
from telegram.ext import ContextTypes

from db.handlers import (
    bank_account_handler, telegram_group_handler, user_group_handler,
)
from utils.account_beautifier import account_beautifier

from ..decorators import admin_only
from ..keyboards import reconcile_kb
from .accounts import get_accounts_command


# === /сверь ===

async def reconciliation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_accounts_command(update, context)
    await update.message.reply_text("Выберите действие:", reply_markup=reconcile_kb())


# === /сверьвсе ===

@admin_only
async def all_chats_reconciliation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    groups_id = [
        ug.group_id for ug in user_group_handler.filter_many(user_id=user_id)
    ]
    groups = telegram_group_handler.filter_many(id=groups_id)
    accounts = bank_account_handler.filter_many(group_id=groups_id)

    accounts_sorted = sorted(accounts, key=lambda a: (a.group_id, a.account_name))
    groups_sorted = sorted(groups, key=lambda g: g.name.lower())

    msg_lines: list[str] = []
    for i, group in enumerate(groups_sorted):
        if i > 0:
            msg_lines.append("")
        msg_lines.append(f"`Чат: {group.name}`")
        tag = str(group.group_tag) if group.group_tag else "-"
        msg_lines.append(f"`Тег: {tag}`")
        group_accounts = [a for a in accounts_sorted if a.group_id == group.id]
        msg_lines.extend(account_beautifier(group_accounts))

    await update.message.reply_text("\n".join(msg_lines), parse_mode="Markdown")