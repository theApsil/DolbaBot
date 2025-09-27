from typing import Protocol, Any

class IExchangeProvider(Protocol):
    async def get_latest(self, symbol: str) -> Any: ...
