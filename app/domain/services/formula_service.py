from app.domain.models.formula import Formula

class FormulaService:
    async def calculate(self, formula: Formula, values: dict[str, float]) -> float:
        # ⚠️ TODO: eval небезопасен, позже заменим на парсер
        expr = formula.expression
        return eval(expr, {}, values)
