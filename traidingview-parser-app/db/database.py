from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from .models import Base
from services.settings import settings
from services.logger import logger


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.schema = None

    def init_database(self, schema: str = None):
        """Инициализация БД с указанием схемы"""
        self.schema = schema

        # Создаем engine
        self.engine = create_engine(settings.database_url)

        # Устанавливаем схему для моделей
        if schema:
            Base.metadata.schema = schema
            for table in Base.metadata.tables.values():
                table.schema = schema

        # Создаем таблицы
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Таблицы созданы в схеме: {schema or 'default'}")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

        # Создаем фабрику сессий
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        """Получение сессии БД"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()


# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()