from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    selenium_url: str = "http://localhost:4444/wd/hub"
    poll_seconds: int = 3
    browser_timeout: int = 60
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    selenium_browser_link: str = "https://example.com"

    # Настройки БД
    database_schema: str = "public"  # Схема по умолчанию
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_outer_port: str
    postgres_db: str

    @property
    def database_url(self) -> str:
        """Динамически создаем database_url из отдельных переменных"""
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_outer_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
