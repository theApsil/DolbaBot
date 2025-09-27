from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"

settings = Settings()

