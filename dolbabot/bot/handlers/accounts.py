from telegram import Update
from telegram.ext import ContextTypes

from db.handlers import bank_account_handler, telegram_group_handler
from utils.account_beautifier import account_beautifier
from utils.logger import logger

from services.accounts import (
    deposit, AccountNotFound, InvalidExpression,
)

from ..constants import Msg
from ..decorators import safe_handler
from ..formatters import format_deposit
from ..keyboards import cancel_tx_kb, statement_kb, delete_account_kb
from .basic import error_command


# === /добавь ===

@safe_handler(Msg.ACC_ADD_ERROR)
async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()[1:]
    user = update.message.from_user
    user_tag = user.username or str(user.id)
    user_id = int(user.id)
    chat_id = update.message.chat_id
    chat_tag = update.message.chat.title or str(update.message.chat.id)

    group = telegram_group_handler.get_one(id=chat_id)
    if not group:
        logger.info(f"ADD: {chat_tag} to database")
        telegram_group_handler.create(
            id=chat_id, name=chat_tag, telegram_tag=user_tag,
        )

    logger.info(f"CONTEXT ARGS {args}")
    if not args:
        await update.message.reply_text(Msg.ACC_NAME_REQUIRED)
        return

    account_name = args[0].lower()
    decimals = 2
    if len(args) > 1:
        try:
            decimals = int(args[1])
        except ValueError:
            await update.message.reply_text(Msg.ACC_DECIMALS_NUMBER)
            return

    if decimals < 0:
        await update.message.reply_text(Msg.ACC_DECIMALS_LOW)
        return
    if decimals > 8:
        await update.message.reply_text(Msg.ACC_DECIMALS_HIGH)
        return

    if bank_account_handler.get_one(account_name=account_name, group_id=chat_id):
        await update.message.reply_text(Msg.ACC_EXISTS)
        return

    bank_account_handler.create(
        account_name=account_name,
        decimals=decimals,
        user_id=user_id,
        group_id=chat_id,
    )
    await update.message.reply_text(
        f"✅ Счёт добавлен. Установлена точность до {decimals} разрядов после запятой."
        if decimals != 2
        else "✅ Счёт добавлен. Установлена точность 2 разряда после запятой. "
             "Иное кол-во разрядов (от 0 до 8) устанавливается добавлением числа в конце команды добавления."
    )


# === /дай ===

@safe_handler(Msg.ACC_LIST_ERROR)
async def get_accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    accounts = bank_account_handler.filter_many(group_id=chat_id)
    if not accounts:
        await update.message.reply_text(Msg.ACC_LIST_EMPTY)
        return

    accounts_sorted = sorted(
        accounts, key=lambda a: (a.group_id, a.account_name)
    )
    msg_lines = ["`Ваших средств:`"] + account_beautifier(accounts_sorted)
    await update.message.reply_text(
        "\n".join(msg_lines),
        reply_markup=statement_kb(),
        parse_mode="Markdown",
    )


# === /<account_name> <expr> ===

@safe_handler(Msg.ACC_MONEY_ERROR)
async def add_money_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await error_command(update, context)
        return

    account_name = parts[0].replace("/", "").lower()
    expression = parts[1].strip()

    try:
        result = deposit(
            group_id=update.message.chat_id,
            account_name=account_name,
            expression=expression,
            user_id=int(update.message.from_user.id),
        )
    except AccountNotFound:
        await update.message.reply_text(
            Msg.ACC_NOT_FOUND.format(name=account_name.upper())
        )
        return
    except InvalidExpression as e:
        await update.message.reply_text(f"❌ Ошибка в выражении: {e}")
        return

    await update.message.reply_text(
        format_deposit(
            result.amount, result.decimals, result.new_balance, result.account_name
        ),
        reply_markup=cancel_tx_kb(result.tx_id),
        parse_mode="Markdown",
    )


# === /удали ===

@safe_handler(Msg.ACC_DELETE_CONF_ERR)
async def delete_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await update.message.reply_text(Msg.ACC_DELETE_NAME_REQ)
        return

    account_name = parts[1].lower()
    chat_id = update.message.chat_id

    account = bank_account_handler.get_one(
        account_name=account_name, group_id=chat_id
    )
    if not account:
        await update.message.reply_text(
            Msg.ACC_NOT_FOUND.format(name=account_name.upper())
        )
        return

    await update.message.reply_text(
        f"Вы уверены, что хотите удалить счёт *{account_name.upper()}* "
        f"и все связанные с ним данные?",
        reply_markup=delete_account_kb(account.id),
        parse_mode="Markdown",
    )