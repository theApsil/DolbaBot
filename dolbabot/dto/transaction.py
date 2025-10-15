from typing import List
from db.models import Transaction, TransactionHistory
from datetime import date

class TransactionDTO:
    @staticmethod
    def from_history(history_items: List[TransactionHistory]) -> List[Transaction]:
        """
        Преобразует список TransactionHistory в список Transaction объектов.
        Все объекты будут созданы в памяти, не сохраняются в БД.
        """
        transactions = []

        for h in history_items:
            t = Transaction(
                id=h.id,  # можно создать новый id, если нужно
                amount=h.amount,
                date=h.date if h.date else date.today(),
                user_request=h.user_request,
                user_id=h.user_id,
                balance=h.balance,
                bank_account_id=h.bank_account_id,
                is_checked=h.is_checked,
                created_at=h.created_at,
            )

            t.user = h.user
            t.bank_account = h.bank_account

            transactions.append(t)

        return transactions