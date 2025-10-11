from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from utils.logger import logger


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.schema = None

    def init_database(self, schema: str = None):
        """Инициализация БД с указанием схемы"""
        self.schema = schema

        self.engine = create_engine(settings.database_url)

        if schema:
            Base.metadata.schema = schema
            for table in Base.metadata.tables.values():
                table.schema = schema

        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Таблицы созданы в схеме: {schema or 'default'}")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        """Получение сессии БД"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()


db_manager = DatabaseManager()