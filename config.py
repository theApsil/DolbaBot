import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

XE_API_USER = os.getenv("XE_API_USER")
XE_API_KEY = os.getenv("XE_API_KEY")

print(XE_API_USER, XE_API_KEY)

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