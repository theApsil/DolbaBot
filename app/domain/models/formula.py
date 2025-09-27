from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass
class Formula:
    id: UUID
    expression: str

    @staticmethod
    def create(expression: str) -> "Formula":
        return Formula(id=uuid4(), expression=expression)
