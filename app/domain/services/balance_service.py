from app.domain.models.balance import Balance
from app.domain.models.transaction import Transaction
from app.domain.repositories.balance_repo import IBalanceRepository
from decimal import Decimal
from typing import List
from uuid import UUID

class BalanceService:
    def __init__(self, repo: IBalanceRepository):
        self.repo = repo

    async def close_day(self) -> List[Balance]:
        """Сводим балансы и возвращаем итог"""
        return await self.repo.get_all()

    async def update_balance(self, balance_id: UUID, delta: Decimal) -> None:
        balance = await self.repo.get_by_id(balance_id)
        if not balance:
            raise ValueError("Balance not found")
        balance.amount += delta
        await self.repo.add(balance)
