from db.database import db_manager
from utils.logger import logger


class BaseHandler:
    model = None  # устанавливается в наследниках

    def __init__(self):
        if self.model is None:
            raise ValueError("Не указан атрибут model в наследуемом классе")

    @staticmethod
    def get_session():
        return db_manager.get_session()

    def create(self, **fields):
        session = self.get_session()
        try:
            obj = self.model(**fields)
            session.add(obj)
            session.commit()
            session.refresh(obj)  # подтягиваем актуальные данные
            session.expunge(obj)   # отвязываем объект
            return obj
        except Exception as e:
            logger.error(f"Ошибка при создании {self.model.__name__}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()

    def get_one(self, **filters):
        session = self.get_session()
        try:
            obj = session.query(self.model).filter_by(**filters).first()
            if not obj:
                return None

            session.expunge(obj)
            return obj
        except Exception as e:
            logger.error(f"Ошибка при получении {self.model.__name__}: {e}")
            raise e
        finally:
            session.close()

    def get_all(self):
        session = self.get_session()
        try:
            objs = session.query(self.model).all()
            session.expunge_all()
            return objs
        except Exception as e:
            logger.error(f"Ошибка при получении всех {self.model.__name__}: {e}")
            raise e
        finally:
            session.close()

    def filter_many(self, **filters):
        """Фильтрация с поддержкой оператора IN для массивов"""
        session = self.get_session()
        try:
            query = session.query(self.model)

            for key, value in filters.items():
                if isinstance(value, (list, tuple, set)):
                    # Используем IN для массивов
                    column = getattr(self.model, key)
                    query = query.filter(column.in_(value))
                else:
                    # Обычный фильтр
                    query = query.filter(getattr(self.model, key) == value)

            objs = query.all()
            session.expunge_all()
            return objs
        except Exception as e:
            logger.error(f"Ошибка при фильтрации {self.model.__name__}: {e}")
            raise e
        finally:
            session.close()

    def update(self, filters: dict, updates: dict):
        session = self.get_session()
        try:
            obj = session.query(self.model).filter_by(**filters).first()
            if not obj:
                return None

            for key, value in updates.items():
                setattr(obj, key, value)

            session.commit()
            session.refresh(obj)
            session.expunge(obj)
            return obj
        except Exception as e:
            logger.error(f"Ошибка при обновлении {self.model.__name__}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self, **filters):
        session = self.get_session()
        try:
            obj = session.query(self.model).filter_by(**filters).first()
            if not obj:
                return False

            session.delete(obj)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении {self.model.__name__}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_many(self, **filters):
        session = self.get_session()
        try:
            objs = session.query(self.model).filter_by(**filters).all()
            if not objs:
                return 0  # ничего не удалили

            count = len(objs)
            for obj in objs:
                session.delete(obj)

            session.commit()
            return count
        except Exception as e:
            logger.error(f"Ошибка при массовом удалении {self.model.__name__}: {e}")
            session.rollback()
            raise e
        finally:
            session.close()
