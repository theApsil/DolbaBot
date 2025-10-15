import os


class Config:
    def __init__(self):
        self.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

        self.CURRENCYLAYER_KEY = os.getenv("CURRENCYLAYER_KEY")

        self.POSTGRES = {
            "user": os.getenv("POSTGRES_USER", "bot_user"),
            "password": os.getenv("POSTGRES_PASSWORD", "bot_password"),
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_CONNECTION_PORT", "5432"),
            "db": os.getenv("POSTGRES_DB", "bot_db"),
        }

        self.DATABASE_URL = (
            f"postgresql+psycopg2://{self.POSTGRES['user']}:{self.POSTGRES['password']}"
            f"@{self.POSTGRES['host']}:{self.POSTGRES['port']}/{self.POSTGRES['db']}"
        )

        self.EXCEL_PATH = os.getenv("EXCEL_PATH")

        self.TRAIDINGVIEW_FASTAPI_APP_LINK = os.getenv("TRAIDINGVIEW_FASTAPI_APP_LINK")
        self.CURRENCYLAYER_URL = os.getenv("CURRENCYLAYER_URL", "https://api.currencylayer.com")
        self.GRINEX_URL = os.getenv("GRINEX_URL", "https://grinex.io/api/v1/spot/depth?symbol=usdta7a5")

config = Config()