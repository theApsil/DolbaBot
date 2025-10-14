from db.models import RegionIndex, Group, User, BankAccount, Transaction, TransactionHistory
from db.handlers.base_handler import BaseHandler


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

class TransactionHistoryHandler(BaseHandler):
    model = TransactionHistory

region_index_handler = RegionIndexHandler()
telegram_group_handler = TelegramGroupHandler()
telegram_user_handler = TelegramUserHandler()
bank_account_handler = BankAccountHandler()
transaction_handler = TransactionHandler()
transaction_history_handler = TransactionHistoryHandler()