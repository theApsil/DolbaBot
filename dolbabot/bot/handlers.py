from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, TypeHandler, ContextTypes
from telegram import Update, InlineKeyboardMarkup
from datetime import datetime
import re
from exchanges.grinex import get_courses_from_grinex, normalize_grinex_data
from exchanges.rapira import get_courses_from_rapira, normalize_rapira_data
from exchanges.traidingview import get_courses_from_tv
from exchanges.base import CurrencyLayerExchange
from services.excel_worker import create_dataframe_from_object, create_temp_excel_file
from .commands import (help_command,
                       kurs_command,
                       pair_command,
                       start_command,
                       calc_command,
                       add_account_command,
                       get_accounts_command,
                       add_money_command,
                       reconciliation_command,
                       delete_account_command,
                       )
from db.handlers.model_handlers import (transaction_handler,
                                        bank_account_handler,
                                        transaction_history_handler)
from utils.logger import logger
from dto.transaction import TransactionDTO
from middlewares.user_exist_middleware import user_middleware
from middlewares.group_exist_middleware import group_middleware

exchange = CurrencyLayerExchange()


# === Обработка всех Inline-кнопок связанных с курсом ===
async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
    r_ask, r_bids = get_courses_from_rapira()
    g_ask, g_bids = get_courses_from_grinex()

    r_ask = r_ask[5:10]
    # === 1. Обновление всех курсов ===
    if data == "refresh_all":
        tv_req = get_courses_from_tv()
        tv_msg = tv_req["course"]

        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask) + f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 *КУРСЫ* _(обновлено {dt})_\n\n"
            f"*RAPIRA* — [ссылка](https://rapira.net/exchange/USDT_RUB)\n{rapira_msg}\n\n"
            f"*GRINEX* — [ссылка](https://grinex.io/trading/usdta7a5)\n{grinex_msg}\n\n"
            f"*TRADINGVIEW* — [ссылка](https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW)\n🇰🇷KRW/USDT — {tv_msg}"
        )

        await query.message.reply_text(msg,
                                      parse_mode="Markdown",
                                       disable_web_page_preview=True
                                       )
        return

    # === 2. Обновление RUB / USDT / WON ===
    if data in ["refresh_usdt", "refresh_rub", "refresh_won"]:
        arg = data.split("_")[1]

        if arg == "usdt":
            msg = (
                f"💵 *КУРС USDT → RUB* _(обновлено {dt})_\n\n"
                f"*RAPIRA*\n🇺🇸USDT/RUB: {r_bids}\n\n"
                f"*GRINEX*\n🇺🇸USDT/RUB: {g_bids}"
            )
        elif arg == "rub":
            msg = (
                f"💱 *СТАКАН RUB → USDT* _(обновлено {dt})_\n\n"
                f"*RAPIRA*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_rapira_data(r_ask)}\n\n"
                f"*GRINEX*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_grinex_data(g_ask)}\n\n"
            )
        else:  # won
            tv_req = get_courses_from_tv()
            tv_msg = tv_req["course"]
            tv_time = datetime.fromisoformat(tv_req["time"]).strftime("%d.%m %H:%M UTC")

            msg = f"🇰🇷 *КУРС USDT → KRW* _(обновлено {tv_time})_\n{tv_msg}"

        await query.message.reply_text(msg,
                                        parse_mode="Markdown",
                                        disable_web_page_preview=True)
        return

    # === 3. Обновление валютной пары (EURUSD и т.д.) ===
    if data.startswith("refresh_") and len(data.split("_")) == 3:
        try:
            _, pair, amount = data.split("_")
            base, quote = pair[:3], pair[3:]
            amount = float(amount)
            result = exchange.convert(base, quote, amount)
            msg = (
                f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
                f"1 {base} = {result['rate']:.5f} {quote}\n"
                f"_(обновлено {dt})_ через currencylayer.com"
            )
            await query.message.reply_text(msg,
                                            parse_mode="Markdown",
                                            disable_web_page_preview=True)
        except Exception as e:
            await query.message.reply_text(f"⚠ Ошибка при обновлении курса: {e}")
        return


async def cancel_transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        data = query.data
        if not data.startswith("cancel_"):
            return

        transaction_id = data.split("_", 1)[1]
        logger.info(f"[transaction_id]: {transaction_id}")
        # === 1. Получаем транзакцию ===
        transaction = transaction_handler.get_one(id=transaction_id)
        if not transaction:
            await query.edit_message_text("⚠️ Транзакция не найдена.")
            return

        if transaction.is_checked:
            await query.edit_message_text("❌ Транзакция уже сверена и не может быть отменена.")
            return

        # === 2. Получаем счёт ===
        account = bank_account_handler.get_one(id=transaction.bank_account_id)
        if not account:
            await query.edit_message_text("⚠️ Счёт, связанный с транзакцией, не найден.")
            return

        # === 3. Откатываем баланс ===
        new_balance = (account.amount or 0) - transaction.amount
        bank_account_handler.update(
            filters={"id": account.id},
            updates={"amount": new_balance},
        )

        # === 4. Обновляем транзакцию ===
        transaction_handler.update(
            filters={"id": transaction.id},
            updates={"user_request": f"[Отмена] {transaction.user_request}"},
        )

        # === 5. Обновляем сообщение ===
        formatted_amount = f"{transaction.amount:,.{account.decimals}f}".replace(",", "’")
        formatted_balance = f"{new_balance:,.{account.decimals}f}".replace(",", "’")

        cancel_time = datetime.now().strftime("%d.%m %H:%M")
        msg = (
            f"❌ Отменено {cancel_time}\n"
            f"−{formatted_amount}\n"
            f"Баланс: {formatted_balance} {account.account_name.upper()}\n"
        )

        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=None)

    except Exception as e:
        logger.error(f"Ошибка при отмене транзакции: {e}")
        await query.edit_message_text("⚠️ Ошибка при отмене транзакции.")


async def reconciliation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    try:
        # === Отмена сверки ===
        if data == "reconcile_cancel":
            await query.edit_message_text("❌ Сверка отменена.")
            return

        # === Подтверждение сверки ===
        if data == "reconcile_confirm":
            count = 0
            logger.info(f"[GROUP]: {query.message.chat.id}")
            accounts = bank_account_handler.filter_many(group_id=query.message.chat.id)
            for account in accounts:
                count += transaction_handler.transfer_to_history(
                    filters={
                        "is_checked": False,
                        "bank_account_id": account.id
                    },
                )

            await query.edit_message_text(f"✅ Балансы сверены. ({count} транзакций отмечено)")
            return

    except Exception as e:
        logger.error(f"Ошибка при сверке: {e}")
        await query.edit_message_text("⚠️ Ошибка при сверке балансов.")


async def delete_account_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query

        await query.answer()

        data = query.data
        logger.info(f"[DATA]: {data}")
        # Отмена
        if data == "account_delete_cancel":
            await query.edit_message_text("❎ Удаление отменено.")
            return

        # Подтверждение
        if data.startswith("account_delete_confirm_"):
            account_id = data.split("_")[-1]
            account = bank_account_handler.get_one(id=account_id)

            if not account:
                await query.edit_message_text("⚠️ Счёт уже удалён или не найден.")
                return

            deleted = bank_account_handler.delete(id=account_id)
            if deleted:
                await query.edit_message_text(
                    f"🗑 Счёт *{account.account_name.upper()}* и все связанные данные удалены.",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text("⚠️ Не удалось удалить счёт.")

    except Exception as e:
        logger.error(f"Ошибка при подтверждении удаления счёта: {e}")
        await update.callback_query.edit_message_text("⚠️ Произошла ошибка при удалении счёта.")


async def create_bank_statement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        logger.info(f"[DATA]: {data}")
        # Отмена
        transactions = []
        statement_type = ""

        if data == "statement_current":
            transactions = transaction_handler.get_all_with_joins(
                filters={"is_checked": False,
                         "group.id": query.message.chat.id},
            )
            statement_type = "Текущая"

        if data == "statement_full":
            transactions = transaction_handler.get_all_with_joins(
                filters={
                         "group.id": query.message.chat.id
                },
            )
            transactions_history = transaction_history_handler.get_all_with_joins(
                filters={
                    "group.id": query.message.chat.id
                },
            )
            statement_type = "Полная"

            transactions = transactions + TransactionDTO.from_history(transactions_history)
        if len(transactions) == 0:
            await query.message.reply_text("⚠️ Нет данных для выписки.")
            return

        transactions = sorted(transactions, key=lambda t: t.created_at, reverse=True)

        df = create_dataframe_from_object(transactions)
        bytes_io = create_temp_excel_file(df)
        date = datetime.now().strftime("%d_%m_%Y")
        await query.message.reply_document(
            document=bytes_io,
            filename=f"{statement_type}_выписка_на_{date}_{query.message.chat.id}.xlsx"
        )

    except Exception as e:
        logger.error(f"Ошибка при создании выписки: {e}")
        await update.callback_query.edit_message_text("⚠️ Произошла ошибка при создании выписки.")


# === Регистрация всех хэндлеров ===
def register_handlers(app):
    app.add_handler(TypeHandler(object, group_middleware), group=-2)
    app.add_handler(TypeHandler(object, user_middleware), group=-1)

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs_command))
    app.add_handler(CommandHandler("add", add_account_command))
    app.add_handler(CommandHandler("give", get_accounts_command))
    app.add_handler(CommandHandler("money", add_money_command))
    app.add_handler(CommandHandler("reconciliation", reconciliation_command))
    app.add_handler(CommandHandler("delete", delete_account_command))

    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(старт|start)\b", re.IGNORECASE)), start_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(помоги|help)\b", re.IGNORECASE)), help_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(дай|give)\b", re.IGNORECASE)), get_accounts_command))
    app.add_handler(MessageHandler(filters.Regex(r"^/[a-zA-Z]{6}\b"), pair_command))
    app.add_handler(MessageHandler(filters.Regex(r"^/[a-zA-Z]{1,50}\b"), add_money_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(курс|kurs)\b", re.IGNORECASE)), kurs_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(добавь|add)\b", re.IGNORECASE)), add_account_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(сверь|reconciliation)\b", re.IGNORECASE)), reconciliation_command))
    app.add_handler(MessageHandler(filters.Regex(re.compile(r"^/(удали|delete)\b", re.IGNORECASE)), delete_account_command))

    app.add_handler(CallbackQueryHandler(refresh_callback, pattern=r"^refresh_"))
    app.add_handler(CallbackQueryHandler(cancel_transaction_callback, pattern=r"^cancel_"))
    app.add_handler(CallbackQueryHandler(reconciliation_callback, pattern=r"^reconcile_"))
    app.add_handler(CallbackQueryHandler(delete_account_callback, pattern=r"^(account_delete_)"))
    app.add_handler(CallbackQueryHandler(create_bank_statement, pattern=r"^(statement_)"))

    app.add_handler(MessageHandler(filters.Regex(r"^/[^a-zA-Z]"), calc_command))
