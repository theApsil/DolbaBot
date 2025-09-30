import re


#FIXME: Неверно определяет процент
#FIXME: Требует скобки в выражении
class Calculator:
    @staticmethod
    def evaluate(expression: str) -> float:
        """
        Вычисляет математическое выражение.
        Поддерживает +, -, *, /, скобки и проценты.
        """
        # заменяем проценты (50% -> (50/100))
        expression = re.sub(r'(\d+(\.\d+)?)%', r'(\1/100)', expression)

        # разрешаем только допустимые символы
        if not re.match(r'^[\d\.\+\-\*/\(\)\s]+$', expression):
            raise ValueError("Недопустимые символы в выражении")

        try:
            result = eval(expression, {"__builtins__": {}})
        except Exception:
            raise ValueError("Ошибка вычисления")

        return round(float(result), 6)
