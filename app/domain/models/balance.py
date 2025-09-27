from dataclasses import dataclass
from uuid import UUID, uuid4
from decimal import Decimal

@dataclass
class Balance:
    id: UUID
    currency: str
    amount: Decimal

    @staticmethod
    def create(currency: str, amount: Decimal) -> "Balance":
        return Balance(id=uuid4(), currency=currency, amount=amount)
