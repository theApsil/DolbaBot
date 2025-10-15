from sqlalchemy.orm import joinedload
from db.models import RegionIndex, Group, User, BankAccount, Transaction, TransactionHistory
from db.handlers.base_handler import BaseHandler
from utils.logger import logger

class RegionIndexHandler(BaseHandler):
    model = RegionIndex

class TelegramGroupHandler(BaseHandler):
    model = Group

class TelegramUserHandler(BaseHandler):
    model = User

class BankAccountHandler(BaseHandler):
    model = BankAccount

class TransactionHandler(BaseHandler):
    model = Transaction

    def transfer_to_history(self, filters: dict = None):
        """
        Переносит транзакции из Transaction в TransactionHistory.
        Если передан filters, переносит только подходящие записи.
        После переноса удаляет их из Transaction.

        Возвращает список созданных объектов TransactionHistory.
        """
        session = self.get_session()
        count = 0
        try:
            query = session.query(Transaction)
            if filters:
                query = query.filter_by(**filters)

            transactions = query.all()
            if not transactions:
                return 0

            history_objects = []
            for tx in transactions:
                count += 1
                # создаём копию для истории
                history_tx = TransactionHistory(
                    id=tx.id,
                    amount=tx.amount,
                    date=tx.date,
                    user_request=tx.user_request,
                    user_id=tx.user_id,
                    balance=tx.balance,
                    bank_account_id=tx.bank_account_id,
                    is_checked=True
                )
                session.add(history_tx)
                history_objects.append(history_tx)

                # удаляем исходную транзакцию
                session.delete(tx)

            session.commit()

            # отвязываем объекты
            for obj in history_objects:
                session.expunge(obj)

            return count

        except Exception as e:
            logger.error(f"Ошибка при переносе транзакций в историю: {e}")
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_with_joins(self, filters: dict = None):
        session = self.get_session()
        try:
            query = (
                session.query(Transaction)
                .options(
                    joinedload(Transaction.user),
                    joinedload(Transaction.bank_account).joinedload(BankAccount.group)
                )
            )

            if filters:
                for key, value in filters.items():
                    if "." in key:
                        # Формат: model.field
                        model_name, field_name = key.split(".", 1)

                        if model_name == "transaction":
                            model = Transaction
                        elif model_name == "bank_account":
                            model = BankAccount
                        elif model_name == "group":
                            model = Group
                        elif model_name == "user":
                            model = User
                        else:
                            raise ValueError(f"Неизвестная модель в фильтре: {model_name}")

                        column = getattr(model, field_name, None)
                        if not column:
                            raise ValueError(f"Поле '{field_name}' не найдено в модели {model_name}")

                        query = query.filter(column == value)

                    else:
                        # Без указания модели → считаем, что это Transaction
                        column = getattr(Transaction, key, None)
                        if not column:
                            raise ValueError(
                                f"Поле '{key}' не найдено в Transaction. "
                                f"Укажи модель явно: e.g. 'bank_account.account_name'"
                            )
                        query = query.filter(column == value)

            results = query.all()

            for obj in results:
                session.expunge(obj)

            return results

        except Exception as e:
            logger.error(f"Ошибка при получении транзакций с джойнами: {e}")
            raise e
        finally:
            session.close()

class TransactionHistoryHandler(BaseHandler):
    model = TransactionHistory

    def get_all_with_joins(self, filters: dict = None):
        session = self.get_session()
        try:
            query = (
                session.query(TransactionHistory)
                .options(
                    joinedload(TransactionHistory.user),
                    joinedload(TransactionHistory.bank_account).joinedload(BankAccount.group)
                )
            )

            if filters:
                for key, value in filters.items():
                    if "." in key:
                        # Формат: model.field
                        model_name, field_name = key.split(".", 1)

                        if model_name == "transaction":
                            model = TransactionHistory
                        elif model_name == "bank_account":
                            model = BankAccount
                        elif model_name == "group":
                            model = Group
                        elif model_name == "user":
                            model = User
                        else:
                            raise ValueError(f"Неизвестная модель в фильтре: {model_name}")

                        column = getattr(model, field_name, None)
                        if not column:
                            raise ValueError(f"Поле '{field_name}' не найдено в модели {model_name}")

                        query = query.filter(column == value)

                    else:
                        # Без указания модели → считаем, что это Transaction
                        column = getattr(TransactionHistory, key, None)
                        if not column:
                            raise ValueError(
                                f"Поле '{key}' не найдено в TransactionHistory. "
                                f"Укажи модель явно: e.g. 'bank_account.account_name'"
                            )
                        query = query.filter(column == value)

            results = query.all()

            for obj in results:
                session.expunge(obj)

            return results

        except Exception as e:
            logger.error(f"Ошибка при получении истории транзакций с джойнами: {e}")
            raise e
        finally:
            session.close()

region_index_handler = RegionIndexHandler()
telegram_group_handler = TelegramGroupHandler()
telegram_user_handler = TelegramUserHandler()
bank_account_handler = BankAccountHandler()
transaction_handler = TransactionHandler()
transaction_history_handler = TransactionHistoryHandler()