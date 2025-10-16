from db.models import BankAccount, Group, User
from utils.logger import logger
from sqlalchemy import and_

class JoinableMixin:
    """
    Миксин для поиска с join + фильтрами в формате "model.field".
    Предполагает наличие self.model (SQLAlchemy ORM-модель)
    и метода self.get_session().
    """

    # какие связи подгружаем по умолчанию
    default_joins = []
    default_loads = []

    def get_all_with_joins(self, filters: dict = None):
        session = self.get_session()
        try:
            # 1. Базовый запрос от self.model (Transaction или TransactionHistory)
            query = session.query(self.model)

            # Флаги, нужны ли JOIN
            need_join_bank = False
            need_join_group = False
            need_join_user = False

            # 2. Анализ фильтров — какие JOIN нужны
            if filters:
                for key in filters.keys():
                    if "." in key:
                        model_name, _ = key.split(".", 1)
                        if model_name == "bank_account":
                            need_join_bank = True
                        elif model_name == "group":
                            need_join_bank = True
                            need_join_group = True
                        elif model_name == "user":
                            need_join_user = True

            # Добавляем JOIN'ы
            if need_join_bank:
                query = query.join(self.model.bank_account)
            if need_join_group:
                query = query.join(BankAccount.group)
            if need_join_user:
                query = query.join(self.model.user)

            # 3. Применяем фильтры
            if filters:
                conditions = []
                for key, value in filters.items():
                    if "." in key:
                        model_name, field_name = key.split(".", 1)
                        # определяем модель в фильтре
                        if model_name in ["transaction", "transaction_history"]:
                            model = self.model
                        elif model_name == "bank_account":
                            model = BankAccount
                        elif model_name == "group":
                            model = Group
                        elif model_name == "user":
                            model = User
                        else:
                            raise ValueError(f"Неизвестная модель: {model_name}")

                        column = getattr(model, field_name, None)
                        if column is None:
                            raise ValueError(f"Поле '{field_name}' нет в {model_name}")

                        if isinstance(value, (list, tuple, set)):
                            conditions.append(column.in_(list(value)))
                        else:
                            conditions.append(column == value)
                    else:
                        # поле модели self.model
                        column = getattr(self.model, key, None)
                        if column is None:
                            raise ValueError(f"Поле '{key}' нет в {self.model.__name__}")
                        if isinstance(value, (list, tuple, set)):
                            conditions.append(column.in_(list(value)))
                        else:
                            conditions.append(column == value)

                if conditions:
                    query = query.filter(and_(*conditions))

            # 4. joinedload для связей
            for opt in self.default_loads:
                query = query.options(opt)

            results = query.all()

            # 5. expunge
            for obj in results:
                session.expunge(obj)

            return results

        except Exception as e:
            logger.error(f"Ошибка в get_all_with_joins({self.model.__name__}): {e}")
            raise e
        finally:
            session.close()