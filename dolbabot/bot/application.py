import re
from telegram.ext import (
    MessageHandler, filters, CallbackQueryHandler, TypeHandler,
)

from middlewares.group_exist_middleware import group_middleware
from middlewares.user_exist_middleware import user_middleware
from middlewares.user_group_exist_middleware import user_group_middleware

from .constants import CB

from .handlers.basic           import start_command, help_command, calc_command, slash_dispatch
from .handlers.rates           import kurs_command
from .handlers.accounts        import (
    add_account_command, get_accounts_command, delete_account_command,
)
from .handlers.reconciliation  import (
    reconciliation_command, all_chats_reconciliation_command,
)
from .handlers.groups          import get_groups_command, change_group_tag_command

from .callbacks.rates           import (
    refresh_all_cb, refresh_usdt_cb, refresh_rub_cb,
    refresh_won_cb, refresh_pair_cb,
)
from .callbacks.accounts        import (
    cancel_transaction_callback, delete_account_callback,
)
from .callbacks.reconciliation  import reconciliation_callback
from .callbacks.statements      import create_bank_statement
from .callbacks.groups          import change_tag_callback


# (aliases, handler)
COMMAND_ROUTES = [
    (("старт",    "start"),                start_command),
    (("помоги",   "help"),                 help_command),
    (("дай",      "b"),                   get_accounts_command),
    (("курс",     "kurs"),                 kurs_command),
    (("добавь",   "add"),                  add_account_command),
    (("сверь",    "reconciliation"),       reconciliation_command),
    (("удали",    "delete"),               delete_account_command),
    (("сверьвсе", "reconsilationall"),     all_chats_reconciliation_command),
    (("группы",   "groups"),               get_groups_command),
    (("группа",   "change_group_tag"),     change_group_tag_command),
]

# (pattern, handler)
CALLBACK_ROUTES = [
    (rf"^{CB.REFRESH_ALL}$",   refresh_all_cb),
    (rf"^{CB.REFRESH_USDT}$",  refresh_usdt_cb),
    (rf"^{CB.REFRESH_RUB}$",   refresh_rub_cb),
    (rf"^{CB.REFRESH_WON}$",   refresh_won_cb),
    (CB.REFRESH_PAIR_RE,       refresh_pair_cb),

    (CB.CANCEL_TX_RE,          cancel_transaction_callback),
    (CB.RECONCILE_RE,          reconciliation_callback),
    (CB.ACC_DELETE_RE,         delete_account_callback),
    (CB.STATEMENT_RE,          create_bank_statement),
    (CB.GROUP_TAG_RE,          change_tag_callback),
]


def _aliases_re(*aliases: str) -> re.Pattern:
    body = "|".join(aliases)
    return re.compile(rf"^/({body})\b", re.IGNORECASE)


def register_handlers(app):
    # middlewares
    app.add_handler(TypeHandler(object, group_middleware),      group=-3)
    app.add_handler(TypeHandler(object, user_middleware),       group=-2)
    app.add_handler(TypeHandler(object, user_group_middleware), group=-1)

    # именованные команды
    for aliases, fn in COMMAND_ROUTES:
        app.add_handler(MessageHandler(filters.Regex(_aliases_re(*aliases)), fn))

    # /<account_name> <expr>  или  /<EURUSD>
    app.add_handler(MessageHandler(filters.Regex(r"^/[a-zA-Z]{1,50}\b"), slash_dispatch))

    # callbacks
    for pattern, fn in CALLBACK_ROUTES:
        app.add_handler(CallbackQueryHandler(fn, pattern=pattern))

    # калькулятор /<expr>
    app.add_handler(MessageHandler(filters.Regex(r"^/[^a-zA-Z]"), calc_command))