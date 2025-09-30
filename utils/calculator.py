import re
import ast
import operator as op

# Разрешённые операции для безопасного вычисления
_allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _ast_eval(node):
    if isinstance(node, ast.Expression):
        return _ast_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Недопустимый тип константы")
    if isinstance(node, ast.BinOp):
        left = _ast_eval(node.left)
        right = _ast_eval(node.right)
        oper = type(node.op)
        if oper not in _allowed_operators:
            raise ValueError("Недопустимая операция")
        return _allowed_operators[oper](left, right)
    if isinstance(node, ast.UnaryOp):
        oper = type(node.op)
        if oper not in _allowed_operators:
            raise ValueError("Недопустимая унарная операция")
        return _allowed_operators[oper](_ast_eval(node.operand))
    raise ValueError("Недопустимый узел в выражении")


def safe_compute(expr_str: str) -> float:
    node = ast.parse(expr_str, mode="eval")
    for n in ast.walk(node):
        if isinstance(n, (ast.Call, ast.Name, ast.Attribute, ast.Subscript)):
            raise ValueError("Недопустимые элементы в выражении")
    return float(_ast_eval(node))


_TOKEN_RE = re.compile(r"\d+\.\d+|\d+|[%\+\-\*\/\(\)]")

def tokenize(expr: str):
    return _TOKEN_RE.findall(expr.replace(" ", ""))


def find_operand_start(tokens, end):
    """
    (оставляем на случай использования) — ищет начало операнда,
    но в логике процентов для + / - мы используем весь левый префикс (см. ниже).
    """
    if tokens[end] == ")":
        bal, i = 0, end
        while i >= 0:
            if tokens[i] == ")":
                bal += 1
            elif tokens[i] == "(":
                bal -= 1
                if bal == 0:
                    start = i
                    break
            i -= 1
    else:
        start = end
    while start - 1 >= 0 and tokens[start - 1] in ("*", "/"):
        prev_end = start - 2
        if prev_end < 0:
            break
        prev_start = find_operand_start(tokens, prev_end)
        start = prev_start
    return start


def transform_percent_logic(expr: str) -> str:
    """
    Основная логика трансформации процентов:
    - Для шаблонов A +/- B% заменяем B% на (A * B / 100), где A — всё левое выражение.
      Т.е. (25-5)-40% -> (25-5) - ((25-5)*40/100)
    - Остальные N% или (expr)% -> (N/100) или ((expr)/100)
    """
    s = expr.replace(" ", "")
    tokens = tokenize(s)

    # 1) Обработка случаев A +/- B%
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("+", "-"):
            # проверяем, что справа число и следом '%'
            if i + 2 < len(tokens) and re.fullmatch(r"\d+(\.\d+)?", tokens[i + 1]) and tokens[i + 2] == "%":
                # **ВАЖНО**: берем в качестве A весь левый префикс (от начала выражения до оператора)
                left_start = 0
                left_end = i - 1
                if left_end < left_start:
                    # нет левой части — пропускаем (на случай некорректного выражения)
                    i += 1
                    continue
                left_tokens = tokens[left_start:left_end + 1]
                op = tok
                percent_number = tokens[i + 1]
                # формируем замену: (<left>) op ((<left>) * percent / 100)
                new_tokens = []
                new_tokens.append("(")
                new_tokens.extend(left_tokens)
                new_tokens.append(")")
                new_tokens.append(op)
                new_tokens.append("(")
                new_tokens.append("(")
                new_tokens.extend(left_tokens)
                new_tokens.append(")")
                new_tokens.append("*")
                new_tokens.append(percent_number)
                new_tokens.append("/")
                new_tokens.append("100")
                new_tokens.append(")")
                # заменяем сегмент tokens[left_start : i+3] (включая '%')
                tokens = new_tokens + tokens[i + 3 :]
                # теперь i переходим за созданные токены
                i = len(new_tokens)
                continue
        i += 1

    # 2) Остаточные N% и (expr)%
    i = 0
    while i < len(tokens):
        # number%
        if re.fullmatch(r"\d+(\.\d+)?", tokens[i]) and i + 1 < len(tokens) and tokens[i + 1] == "%":
            new = ["(", tokens[i], "/", "100", ")"]
            tokens = tokens[:i] + new + tokens[i + 2 :]
            i += len(new)
            continue
        # (expr)%
        if tokens[i] == ")" and i + 1 < len(tokens) and tokens[i + 1] == "%":
            # найдём индекс соответствующей '('
            bal = 0
            j = i
            while j >= 0:
                if tokens[j] == ")":
                    bal += 1
                elif tokens[j] == "(":
                    bal -= 1
                    if bal == 0:
                        start = j
                        break
                j -= 1
            inner = tokens[start : i + 1]
            new = ["(", "("] + inner + [")", "/", "100", ")"]
            tokens = tokens[:start] + new + tokens[i + 2 :]
            i = start + len(new)
            continue
        i += 1

    return "".join(tokens)

# FIXME: Некорректная обработка, если процент - перед скобкой
def evaluate(expression: str) -> float:
    if not expression or not expression.strip():
        raise ValueError("Пустое выражение")
    expr = expression.strip().replace(",", ".")
    transformed = transform_percent_logic(expr)
    value = safe_compute(transformed)
    return round(value, 6)
