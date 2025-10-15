import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from exchanges.base import CurrencyLayerExchange
from exchanges.grinex import get_courses_from_grinex, normalize_grinex_data
from exchanges.rapira import get_courses_from_rapira, normalize_rapira_data
from exchanges.traidingview import get_courses_from_tv
from utils.calculator import evaluate
from utils.helpers import escape_md
from services.formulas import usdt, krw, jpy
from utils.rapira_decision import make_decision
from utils.logger import logger
from db.handlers import (telegram_user_handler,
                         bank_account_handler,
                         telegram_group_handler,
                         transaction_handler, region_index_handler)
from telegram import Update


exchange = CurrencyLayerExchange()

HELP_TEXT = """
Доступные команды:
 - /старт — запустить бота
 - /помоги — список команд
 - /курс <пара_валют> <размер или выражение> — курс валют (/курс eurusd 100)
 - /курс — выдает все курсы: rub/usdt, usdt/rub, usdt/won
 - /курс руб — стакан RUB→USDT
 - /курс usdt — курс USDT→RUB
 - /курс вона — курс USDT→KRW
 - /(выражение) — калькулятор
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("```🤖 Бот запущен.```", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)

# === /курс ===
async def kurs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()
    args = text[1:]

    r_ask, r_bids = get_courses_from_rapira()
    actual_tether = make_decision(r_ask)['price']
    logger.info(F"DECISION RAPIRA: {actual_tether}")

    r_ask = r_ask[5:10]
    if not args:
        g_ask, g_bids = get_courses_from_grinex()
        tv_req = get_courses_from_tv()
        tv_msg = tv_req["course"]

        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        rapira_msg = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
        grinex_msg = normalize_grinex_data(g_ask)+ f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"

        msg = (
            f"📊 *КУРСЫ* \({escape_md(dt)}\)\n\n"
            f"*RAPIRA* — [ссылка]({escape_md('https://rapira.net/exchange/USDT_RUB')})\n{escape_md(rapira_msg)}\n\n"
            f"*GRINEX* — [ссылка]({escape_md('https://grinex.io/trading/usdta7a5')})\n{escape_md(grinex_msg)}\n\n"
            f"*TRADINGVIEW* — [ссылка]({escape_md('https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW')})\n🇰🇷KRW/USDT — {escape_md(tv_msg)}"
        )

        keyboard = [[InlineKeyboardButton("🔄 Обновить всё", callback_data="refresh_all")]]
        await update.message.reply_text(msg,
                                        reply_markup=InlineKeyboardMarkup(keyboard),
                                        disable_web_page_preview=True, parse_mode="MarkdownV2")
        return

    arg = args[0].lower()

    # === /курс usdt ===
    if arg in ["usdt", "доллар", "тезер"]:
        new_args = args[1:]
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")

        if new_args:
            city = new_args[0] if len(new_args) > 0 else None
            if city is None:
                await update.message.reply_text("🏙 Укажите город. Пример: `/курс usdt Краснодар 1.2`",
                                                parse_mode="Markdown")
                return

            city = city.title()

            db_city = region_index_handler.get_one(city=city)
            if not db_city:
                await update.message.reply_text(f"❌ Город *{city}* не найден в базе данных.", parse_mode="Markdown")
                return

            index = float(new_args[1]) if len(new_args) > 1 else None
            if index is None:
                await update.message.reply_text("❌ Укажите индекс. Пример: `/курс usdt Краснодар 1.2`",
                                                parse_mode="Markdown")
                return

            # TODO: Нормализация сопоставления городов и их индекса
            course = usdt(actual_tether, city, float(index))

            msg = (
                f"💵 *Объём тезера* _({dt})_\n"
                f"{course[0]} = {course[1]}\n"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        g_ask, g_bids = get_courses_from_grinex()
        msg = (
            f"💵 *КУРС USDT → RUB* _({dt})_\n\n"
            f"*RAPIRA*\n🇺🇸USDT/RUB: {r_bids}\n\n"
            f"*GRINEX*\n🇺🇸USDT/RUB: {g_bids}"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_usdt")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    # === /курс руб ===
    if arg in ["руб", "rub", "ruble"]:
        g_ask, _ = get_courses_from_grinex()
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        msg = (
            f"💱 *СТАКАН RUB → USDT* _({dt})_\n\n"
            f"*RAPIRA*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_rapira_data(r_ask)}\n\n"
            f"*GRINEX*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_grinex_data(g_ask)}\n\n"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_rub")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    # === /курс вона ===
    if arg in ["вона", "won", "krw"]:
        tv_req = get_courses_from_tv()
        tv_msg = tv_req["course"]
        dt = datetime.fromisoformat(tv_req["time"]).strftime("%d.%m %H:%M UTC")
        new_args = args[1:]

        if new_args:
            city = new_args[0] if len(new_args) > 0 else None
            if city is None:
                await update.message.reply_text("🏙 Укажите город. Пример: `/курс usdt Краснодар 1.2`",
                                                parse_mode="Markdown")
                return

            city = city.title()

            db_city = region_index_handler.get_one(city=city)
            if not db_city:
                await update.message.reply_text(f"❌ Город *{city}* не найден в базе данных.", parse_mode="Markdown")
                return

            index = float(new_args[1]) if len(new_args) > 1 else None
            if index is None:
                await update.message.reply_text("❌ Укажите индекс. Пример: `/курс usdt Краснодар 1.2`",
                                                parse_mode="Markdown")
                return
            city = city.title()
            # TODO: Нормализация сопоставления городов и их индекса
            won = krw(actual_tether, city, tv_msg, float(index))
            msg = (
                f"🇰🇷 *КУРС USDT → KRW* _({dt})_\n"
                f"{won[0]} = {won[1]}\n"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        msg = f"🇰🇷 *КУРС USDT → KRW* _({dt})_\n{tv_msg}"
        kb = [[InlineKeyboardButton("🔄 Обновить", callback_data="refresh_won")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if arg in ["йена", "jpy"]:
        dt = datetime.utcnow().strftime("%d.%m %H:%M UTC")
        new_args = args[1:]
        if not new_args or len(new_args) != 3:
            msg = (
                f"Ошибка при указании параметров рассчёта курса. Повторите запрос с корректным количеством параметров\n"
                f"Например: `/курс йена Краснодар 145.6 1`\n"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return
        else:
            city = new_args[0] if len(new_args) > 0 else None
            if city is None:
                await update.message.reply_text("🏙 Укажите город. Пример: `/курс usdt Краснодар 1.2`",
                                                parse_mode="Markdown")
                return

            city = city.title()

            db_city = region_index_handler.get_one(city=city)
            if not db_city:
                await update.message.reply_text(f"❌ Город *{city}* не найден в базе данных.", parse_mode="Markdown")
                return

            index = float(new_args[2]) if len(new_args) > 1 else None
            if index is None:
                await update.message.reply_text("❌ Укажите индекс. Пример: `/курс usdt Краснодар 1.2`",
                                                parse_mode="Markdown")
                return
            tether = float(new_args[1])
            # TODO: Нормализация сопоставления городов и их индекса

            jpy_msg = jpy(actual_tether, city, tether, index)
            msg = (
                f"🇯🇵 *USDT → JPY* _(обновлено {dt})_\n"
                f"{jpy_msg[0]} = {jpy_msg[1]}\n"
                f"*КУРС:* _{round(jpy_msg[1] * 100, 2)}_"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

    # === Валютная пара ===
    raw_pair = re.sub(r'[^A-Za-z]', '', arg).upper()
    if len(raw_pair) < 6:
        await update.message.reply_text("❌ Неверная пара. Пример: EURUSD")
        return

    base, quote = raw_pair[:3], raw_pair[3:6]
    expr = " ".join(args[1:]) if len(args) > 1 else "1"

    try:
        amount = evaluate(expr)
        result = exchange.convert(base, quote, amount)
        dt = datetime.utcfromtimestamp(result["timestamp"]).strftime("%d.%m %H:%M UTC")

        msg = (
            f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
            f"1 {base} = {result['rate']:.5f} {quote}\n"
            f"at {dt} currencylayer.com"
        )
        kb = [[InlineKeyboardButton("🔄 Обновить курс", callback_data=f"refresh_{base}{quote}_{amount}")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"⚠ Ошибка при получении курса: {e}")


async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lstrip("/")
    parts = text.split(maxsplit=1)
    raw_pair = parts[0]
    pair_clean = re.sub(r'[^A-Za-z]', '', raw_pair).upper()
    if len(pair_clean) < 6:
        await update.message.reply_text("❌ Неверная пара. Пример: /eurusd 100")
        return
    base, quote = pair_clean[:3], pair_clean[3:6]

    expr = parts[1] if len(parts) > 1 else "1"
    try:
        amount = evaluate(expr)
    except Exception as e:
        await update.message.reply_text(f"Ошибка в выражении суммы: {e}")
        return

    try:
        result = exchange.convert(base, quote, amount)
        dt = datetime.utcfromtimestamp(result['timestamp']).strftime("%d.%m %H:%M UTC")

        msg = (
            f"{result['converted']:.3f} {quote} = ({amount}) {base}\n"
            f"1 {base} = {result['rate']:.5f} {quote}\n"
            f"at {dt} currencylayer.com"
        )

        keyboard = [
            [InlineKeyboardButton("🔄 Обновить курс", callback_data=f"refresh_{base}{quote}_{amount}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    except Exception as e:
        msg = f"⚠ Ошибка при получении курса: {e}"
        reply_markup = None

    await update.message.reply_text(
        msg,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = update.message.text.lstrip("/")
    try:
        result = evaluate(expr)
        await update.message.reply_text(f"{expr} = {result}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


# === /добавь ===
async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()
    args = text[1:]

    try:
        user = update.message.from_user
        user_tag = user.username or str(user.id)
        user_id = int(user.id)
        chat_id = update.message.chat_id
        chat_tag = update.message.chat.title or str(update.message.chat.id)

        # Получаем группу
        group = telegram_group_handler.get_one(id=chat_id)
        if not group:
            logger.info(f"ADD: {chat_tag} to database")
            group = telegram_group_handler.create(
                id=chat_id,
                name=chat_tag,
                telegram_tag=user_tag # TODO: Заменить
            )

        logger.info(f"CONTEXT ARGS {args}")
        if not args:
            await update.message.reply_text("❌ Укажите название счёта. Пример: /добавь usd 2")
            return

        account_name = args[0].lower()
        decimals = 2

        if len(args) > 1: # TODO: Добавить проверку на множественное количество аргументов
            try:
                decimals = int(args[1])
            except ValueError:
                await update.message.reply_text("❌ Точность должна быть числом от 0 до 8.")
                return
        if decimals < 0:
            await update.message.reply_text("❌ Точность не может быть меньше 0.")
            return
        if decimals > 8:
            await update.message.reply_text("❌ Точность не может быть больше 8.")
            return

        existing = bank_account_handler.get_one(account_name=account_name, group_id=group.id)
        if existing:
            await update.message.reply_text("⚠️ Счёт с таким именем уже существует!")
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

    except Exception as e:
        logger.error(f"Ошибка при добавлении счёта: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при добавлении счёта.")


# === /дай ===
async def get_accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id

        accounts = bank_account_handler.filter_many(group_id=chat_id)
        if not accounts:
            await update.message.reply_text("У вас пока нет счетов.")
            return

        msg_lines = ["`Ваших средств:`"]
        for acc in accounts:
            formatted_amount = f"{acc.amount:.{acc.decimals}f}"
            line = f"{formatted_amount} {acc.account_name.upper()}"
            padded_line = line.rjust(30)
            msg_lines.append(f"`{padded_line}`")

        msg = "\n".join(msg_lines)
        keyboard = [
            [
                InlineKeyboardButton("📄 Текущая выписка", callback_data="statement_current"),
                InlineKeyboardButton("📜 Полная выписка", callback_data="statement_full"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msg,
                                        reply_markup=reply_markup,
                                        parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка при получении счетов: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при получении списка счетов.")


# === /<название_счёта> сумма ===
async def add_money_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split(maxsplit=1)

        if len(parts) < 2:
            await update.message.reply_text("❌ Укажите сумму или выражение. Пример: /usd (12*2)+1/3+0.5%")
            return

        account_name = parts[0].replace("/", "").lower()
        expression = parts[1].strip()

        user = update.message.from_user
        user_id = int(user.id)
        chat_id = update.message.chat_id

        # Проверяем наличие счёта
        account = bank_account_handler.get_one(account_name=account_name, group_id=chat_id)
        if not account:
            await update.message.reply_text(f"⚠️ Счёт {account_name.upper()} не найден.")
            return
        decimals = account.decimals
        account_id = account.id
        # === 1. Вычисляем выражение ===
        try:
            amount = round(float(evaluate(expression)), decimals)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка в выражении: {e}")
            return

        # === 2. Обновляем баланс ===
        new_balance = (account.amount or 0) + amount

        bank_account_handler.update(
            filters={
                "group_id": chat_id,
                "account_name": account_name,
            },
            updates={
                "amount": new_balance,
            }
        )

        # === 3. Создаём транзакцию ===
        transaction = transaction_handler.create(
            amount=amount,  # итоговая сумма
            date=datetime.now().date(),
            user_request=expression,  # без /название
            user_id=user_id,
            balance=new_balance,
            bank_account_id=account_id,
            is_checked=False,
        )

        # === 4. Форматируем ответ ===
        formatted_amount = f"{amount:,.{decimals}f}".replace(",", "’")
        formatted_balance = f"{new_balance:,.{decimals}f}".replace(",", "’")

        keyboard = [
            [InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{transaction.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            f"Запомнил. +{formatted_amount}\n"
            f"Баланс: {formatted_balance} {account_name.upper()}\n"
            f"🆔 ID транзакции: `{transaction.id}`"
        )

        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка при добавлении средств: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при добавлении средств.")


# === Сверка балансов ===
async def reconciliation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_accounts_command(update, context)
    keyboard = [
            [
                InlineKeyboardButton("Сверено✅", callback_data="reconcile_confirm"),
                InlineKeyboardButton("Отменить❌", callback_data="reconcile_cancel"),
            ]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


# === /удалить ===
async def delete_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split(maxsplit=1)

        if len(parts) < 2:
            await update.message.reply_text("❌ Укажите название счёта. Пример: /удалить usd")
            return

        account_name = parts[1].lower()
        chat_id = update.message.chat_id

        # Проверяем наличие счёта
        account = bank_account_handler.get_one(account_name=account_name, group_id=chat_id)
        if not account:
            await update.message.reply_text(f"⚠️ Счёт {account_name.upper()} не найден.")
            return

        keyboard = [
            [
                InlineKeyboardButton("✅ Удалить", callback_data=f"account_delete_confirm_{account.id}"),
                InlineKeyboardButton("❌ Отмена", callback_data="account_delete_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Вы уверены, что хотите удалить счёт *{account_name.upper()}* и все связанные с ним данные?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка при запросе подтверждения удаления счёта: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при запросе подтверждения удаления счёта.")
