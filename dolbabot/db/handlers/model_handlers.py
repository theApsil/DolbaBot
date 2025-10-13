from db.models import RegionIndex, Group, User, BankAccount
from db.handlers.base_handler import BaseHandler


class RegionIndexHandler(BaseHandler):
    model = RegionIndex

class TelegramGroupHandler(BaseHandler):
    model = Group

class TelegramUserHandler(BaseHandler):
    model = User

class BankAccountHandler(BaseHandler):
    model = BankAccount

region_index_handler = RegionIndexHandler()
telegram_group_handler = TelegramGroupHandler()
telegram_user_handler = TelegramUserHandler()
bank_account_handler = BankAccountHandler()