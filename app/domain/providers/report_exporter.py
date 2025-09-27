from typing import Protocol, Any

class IReportExporter(Protocol):
    async def export(self, data: list[dict]) -> Any: ...
