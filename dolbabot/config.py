import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

XE_API_USER = os.getenv("XE_API_USER")
XE_API_KEY = os.getenv("XE_API_KEY")

CURRENCYLAYER_KEY = os.getenv("CURRENCYLAYER_KEY")

POSTGRES = {
    "user": os.getenv("POSTGRES_USER", "bot_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "bot_password"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "db": os.getenv("POSTGRES_DB", "bot_db"),
}

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES['user']}:{POSTGRES['password']}"
    f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}"
)

EXCEL_PATH = os.getenv("EXCEL_PATH")

TRAIDINGVIEW_FASTAPI_APP_LINK = os.getenv("TRAIDINGVIEW_FASTAPI_APP_LINK")