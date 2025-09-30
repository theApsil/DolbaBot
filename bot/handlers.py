from telegram.ext import CommandHandler, MessageHandler, filters
from .commands import help_command , kurs_command, pair_command
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from exchanges.base import CurrencyLayerExchange
from datetime import datetime

exchange = CurrencyLayerExchange()


async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # refresh_EURUSD_100
    _, pair, amount = data.split("_")
    base, quote = pair[:3], pair[3:]
    amount = float(amount)

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
        msg = f"⚠ Ошибка при обновлении курса: {e}"
        reply_markup = None

    # Отправляем новое сообщение (а не редактируем старое)
    await query.message.reply_text(
        msg,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

def register_handlers(app):
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs_command))
    # команды вида /eurusd, /usdrub, /btcusdt
    app.add_handler(MessageHandler(filters.COMMAND, pair_command))
