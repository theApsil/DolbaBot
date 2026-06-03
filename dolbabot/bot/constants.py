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
 - /b - вывод всех счетов группы
 - /добавь <счет> <кол-во знаков> - добавить счет с названием <счет> и с количеством знаков. Если знаки не указаны - 2
 - /<счет> <выражение> - добавить на счет результат выражения
 - /удали <счет> - удалить счет
 - /сверь - запустить процедуру сверки счета
Команды администратора:
 - /сверьвсе - показывает сводку балансов по всем счетам всех групп, в которых состоит администратор
 - /группы - показывает группы, в которых состоит пользователь, который вызвал данную команду
 - /группа <ID> <Тег> - меняет тег группе, ID которой указан в команде
"""


class CB:
    """Callback data — все идентификаторы и regex-паттерны."""
    # Курсы
    REFRESH_ALL  = "refresh_all"
    REFRESH_USDT = "refresh_usdt"
    REFRESH_RUB  = "refresh_rub"
    REFRESH_WON  = "refresh_won"
    REFRESH_PAIR_FMT = "refresh_{pair}_{amount}"
    REFRESH_PAIR_RE  = r"^refresh_[A-Za-z]{6}_"

    # Транзакции
    CANCEL_TX_FMT = "cancel_{tx_id}"
    CANCEL_TX_RE  = r"^cancel_"

    # Сверка
    RECONCILE_CONFIRM = "reconcile_confirm"
    RECONCILE_CANCEL  = "reconcile_cancel"
    RECONCILE_RE      = r"^reconcile_"

    # Удаление счёта
    ACC_DELETE_CONFIRM_FMT = "account_delete_confirm_{id}"
    ACC_DELETE_CANCEL      = "account_delete_cancel"
    ACC_DELETE_RE          = r"^account_delete_"

    # Выписка
    STATEMENT_CURRENT = "statement_current"
    STATEMENT_FULL    = "statement_full"
    STATEMENT_RE      = r"^statement_"

    # Тег группы
    GROUP_TAG_CONFIRM = "group_tag_change_confirm"
    GROUP_TAG_CANCEL  = "group_tag_change_cancel"
    GROUP_TAG_RE      = r"^group_tag_change_"


class Urls:
    RAPIRA = "https://rapira.net/exchange/USDT_RUB"
    GRINEX = "https://grinex.io/trading/usdta7a5"
    TV     = "https://ru.tradingview.com/chart/?symbol=BITHUMB%3AUSDTKRW"


class Msg:
    # Общее
    GENERIC_ERROR    = "⚠️ Произошла ошибка."
    UNKNOWN_COMMAND  = "Неизвестная команда. Я таких не знаю. Я глупий."
    NO_ACCESS        = "❌У вас нет доступа к этой команде❌"

    # Аргументы
    CITY_REQUIRED    = "🏙 Укажите город. Пример: `/курс usdt Краснодар 1.2`"
    CITY_NOT_FOUND   = "❌ Город *{city}* не найден в базе данных."
    INDEX_REQUIRED   = "❌ Укажите индекс. Пример: `/курс usdt Краснодар 1.2`"
    INDEX_NOT_NUMBER = "❌ Индекс должен быть числом."
    PAIR_INVALID     = "❌ Неверная пара. Пример: /eurusd 100"

    # Счета
    ACC_NOT_FOUND        = "⚠️ Счёт {name} не найден."
    ACC_EXISTS           = "⚠️ Счёт с таким именем уже существует!"
    ACC_NAME_REQUIRED    = "❌ Укажите название счёта. Пример: /добавь usd 2"
    ACC_DELETE_NAME_REQ  = "❌ Укажите название счёта. Пример: /удалить usd"
    ACC_DECIMALS_NUMBER  = "❌ Точность должна быть числом от 0 до 8."
    ACC_DECIMALS_LOW     = "❌ Точность не может быть меньше 0."
    ACC_DECIMALS_HIGH    = "❌ Точность не может быть больше 8."
    ACC_LIST_EMPTY       = "У вас пока нет счетов."
    ACC_ADD_ERROR        = "⚠️ Произошла ошибка при добавлении счёта."
    ACC_LIST_ERROR       = "⚠️ Произошла ошибка при получении списка счетов."
    ACC_MONEY_ERROR      = "⚠️ Произошла ошибка при добавлении средств."
    ACC_DELETE_CONF_ERR  = "⚠️ Произошла ошибка при запросе подтверждения удаления счёта."

    # Транзакции
    TX_NOT_FOUND         = "⚠️ Транзакция не найдена."
    TX_ALREADY_CHECKED   = "❌ Транзакция уже сверена и не может быть отменена."
    TX_CANCEL_ERROR      = "⚠️ Ошибка при отмене транзакции."
    TX_ACC_MISSING       = "⚠️ Счёт, связанный с транзакцией, не найден."

    # Удаление счёта
    ACC_DELETE_CANCELED  = "❎ Удаление отменено."
    ACC_ALREADY_DELETED  = "⚠️ Счёт уже удалён или не найден."
    ACC_DELETE_FAILED    = "⚠️ Не удалось удалить счёт."

    # Выписка
    STATEMENT_EMPTY      = "⚠️ Нет данных для выписки."
    STATEMENT_ERROR      = "⚠️ Произошла ошибка при создании выписки."

    # Сверка
    RECONCILE_CANCELED   = "❌ Сверка отменена."
    RECONCILE_ERROR      = "⚠️ Ошибка при сверке балансов."

    # Тег группы
    TAG_ARGS_REQUIRED    = "❌ Укажите ID группы и новый тег. Пример: /группа -3145555 #New_Tag"
    TAG_TOO_LONG         = "❌ Нельзя создать тег более 150 символов"
    TAG_MUST_START_HASH  = "❌ Тег должен начинаться со знака #"
    TAG_GROUP_NOT_EXISTS = "❌ Такой группы не существует"
    TAG_USER_NOT_IN      = "❌ Пользователь не состоит в группе, ID которой был введён"
    TAG_CHANGE_CANCELED  = "❎ Изменение отменено."
    TAG_CHANGE_FOREIGN   = "❌ Вы не можете подтвердить, так как сообщение вызвано не вами"
    TAG_CHANGE_ERROR     = "⚠️ Произошла ошибка при изменении тега группы."