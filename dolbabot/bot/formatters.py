from datetime import datetime
from exchanges.grinex import normalize_grinex_data
from exchanges.rapira import normalize_rapira_data
from utils.helpers import escape_md
from .constants import Urls


def utc_now() -> str:
    return datetime.utcnow().strftime("%d.%m %H:%M UTC")


def utc_from_iso(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime("%d.%m %H:%M UTC")


def utc_from_ts(ts: float) -> str:
    return datetime.utcfromtimestamp(ts).strftime("%d.%m %H:%M UTC")


def fmt_amount(value: float, decimals: int) -> str:
    return f"{value:,.{decimals}f}".replace(",", "’")


def fmt_signed(value: float, decimals: int) -> tuple[str, str]:
    sign = "+" if value >= 0 else "−"
    return sign, fmt_amount(abs(value), decimals)


# ----- Курсы -----

def format_all_rates_md_v2(r_ask, r_bids, g_ask, g_bids, tv_msg) -> str:
    """Используется в `/курс` (MarkdownV2)."""
    dt = utc_now()
    rapira_block = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
    grinex_block = normalize_grinex_data(g_ask) + f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"
    return (
        f"📊 *КУРСЫ* \({escape_md(dt)}\)\n\n"
        f"*RAPIRA* — [ссылка]({escape_md(Urls.RAPIRA)})\n{escape_md(rapira_block)}\n\n"
        f"*GRINEX* — [ссылка]({escape_md(Urls.GRINEX)})\n{escape_md(grinex_block)}\n\n"
        f"*TRADINGVIEW* — [ссылка]({escape_md(Urls.TV)})\n🇰🇷KRW/USDT — {escape_md(tv_msg)}"
    )


def format_all_rates(r_ask, r_bids, g_ask, g_bids, tv_msg) -> str:
    """Используется в refresh-callback (обычный Markdown)."""
    dt = utc_now()
    rapira_block = normalize_rapira_data(r_ask) + f"\n==================\n🇺🇸USDT/RUB: {r_bids}\n"
    grinex_block = normalize_grinex_data(g_ask) + f"\n==================\n🇺🇸USDT/RUB: {g_bids}\n"
    return (
        f"📊 *КУРСЫ* _(обновлено {dt})_\n\n"
        f"*RAPIRA* — [ссылка]({Urls.RAPIRA})\n{rapira_block}\n\n"
        f"*GRINEX* — [ссылка]({Urls.GRINEX})\n{grinex_block}\n\n"
        f"*TRADINGVIEW* — [ссылка]({Urls.TV})\n🇰🇷KRW/USDT — {tv_msg}"
    )


def format_usdt_rub(r_bids, g_bids) -> str:
    return (
        f"💵 *КУРС USDT → RUB* _(обновлено {utc_now()})_\n\n"
        f"*RAPIRA*\n🇺🇸USDT/RUB: {r_bids}\n\n"
        f"*GRINEX*\n🇺🇸USDT/RUB: {g_bids}"
    )


def format_rub_usdt(r_ask, g_ask) -> str:
    return (
        f"💱 *СТАКАН RUB → USDT* _(обновлено {utc_now()})_\n\n"
        f"*RAPIRA*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_rapira_data(r_ask)}\n\n"
        f"*GRINEX*\n🇷🇺Цена RUB\t\tОбъём USDT\n{normalize_grinex_data(g_ask)}\n\n"
    )


def format_won(tv_msg: str, dt: str) -> str:
    return f"🇰🇷 *КУРС USDT → KRW* _(обновлено {dt})_\n{tv_msg}"


def format_pair(base: str, quote: str, amount: float,
                converted: float, rate: float, dt: str | None = None) -> str:
    dt = dt or utc_now()
    return (
        f"{converted:.3f} {quote} = ({amount}) {base}\n"
        f"1 {base} = {rate:.5f} {quote}\n"
        f"at {dt} currencylayer.com"
    )


# ----- Транзакции -----

def format_tx_cancel(amount: float, decimals: int, new_balance: float,
                     account_name: str, user_tag: str) -> str:
    sign = "−" if amount >= 0 else "+"  # инвертируем — откатываем
    cancel_time = datetime.now().strftime("%d.%m %H:%M")
    return (
        f"❌ Отменено {cancel_time} by @{user_tag}\n"
        f"{sign}{fmt_amount(abs(amount), decimals)}\n"
        f"Баланс: {fmt_amount(new_balance, decimals)} {account_name.upper()}\n"
    )


def format_deposit(amount: float, decimals: int, new_balance: float,
                   account_name: str) -> str:
    sign, abs_str = fmt_signed(amount, decimals)
    return (
        f"Запомнил. {sign}{abs_str}\n"
        f"Баланс: {fmt_amount(new_balance, decimals)} {account_name.upper()}"
    )