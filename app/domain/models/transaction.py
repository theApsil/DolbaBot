from dataclasses import dataclass
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

@dataclass
class Transaction:
    id: UUID
    balance_id: UUID
    amount: Decimal
    timestamp: datetime

    @staticmethod
    def create(balance_id: UUID, amount: Decimal) -> "Transaction":
        return Transaction(
            id=uuid4(),
            balance_id=balance_id,
            amount=amount,
            timestamp=datetime.utcnow(),
        )
