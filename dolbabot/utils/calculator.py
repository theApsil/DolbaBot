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
_TOKEN_RE = re.compile(r"\d+\.\d+|\d+|[%\+\-\*\/\(\)]")


def safe_compute(expr_str: str) -> float:
    node = ast.parse(expr_str, mode="eval")
    for n in ast.walk(node):
        if isinstance(n, (ast.Call, ast.Name, ast.Attribute, ast.Subscript)):
            raise ValueError("Недопустимые элементы в выражении")
    return float(_ast_eval(node))



def tokenize(expr: str):
    return _TOKEN_RE.findall(expr.replace(" ", ""))


def transform_percent_logic(expr: str) -> str:
    """
    Преобразует выражение так, чтобы проценты считались правильно:
    - A +/- B% -> A +/- ((A) * B / 100)  (A — весь левый префикс, ограниченный ближайшей открывающей '(' если есть)
    - N% -> (N/100)
    - (expr)% -> ((expr)/100)
    """
    s = expr.replace(" ", "")
    tokens = tokenize(s)

    # 1) Обработка случаев A +/- B%
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("+", "-"):
            if i + 2 < len(tokens) and re.fullmatch(r"\d+(\.\d+)?", tokens[i + 1]) and tokens[i + 2] == "%":
                # left_end — индекс токена слева от оператора
                left_end = i - 1
                if left_end < 0:
                    i += 1
                    continue

                # Найти границу текущей группы: ищем ближайшую '(' влево,
                # которая не была закрыта ')' между ней и оператором.
                # Если такой '(' найден — левый префикс начинается после неё,
                # иначе — с начала выражения (индекс 0).
                bal = 0
                left_start = None
                j = left_end
                while j >= 0:
                    if tokens[j] == ")":
                        bal += 1
                    elif tokens[j] == "(":
                        if bal > 0:
                            bal -= 1
                        else:
                            # нашли незакрытую '(' — граница группы
                            left_start = j + 1
                            break
                    j -= 1
                if left_start is None:
                    left_start = 0

                left_tokens = tokens[left_start:left_end + 1]
                op = tok
                percent_number = tokens[i + 1]

                # строим замену: (<left>) op ((<left>) * percent / 100)
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

                # заменяем сегмент tokens[left_start : i+3] включая '%'
                tokens = tokens[:left_start] + new_tokens + tokens[i + 3 :]
                # поставим i сразу после вставленных токенов
                i = left_start + len(new_tokens)
                continue
        i += 1

    # 2) Преобразуем оставшиеся N% и (expr)%
    i = 0
    while i < len(tokens):
        if re.fullmatch(r"\d+(\.\d+)?", tokens[i]) and i + 1 < len(tokens) and tokens[i + 1] == "%":
            new = ["(", tokens[i], "/", "100", ")"]
            tokens = tokens[:i] + new + tokens[i + 2 :]
            i += len(new)
            continue
        if tokens[i] == ")" and i + 1 < len(tokens) and tokens[i + 1] == "%":
            # найдём индекс соответствующей '('
            bal = 0
            j = i
            start = None
            while j >= 0:
                if tokens[j] == ")":
                    bal += 1
                elif tokens[j] == "(":
                    bal -= 1
                    if bal == 0:
                        start = j
                        break
                j -= 1
            if start is None:
                raise ValueError("Несбалансированные скобки при обработке процента")
            inner = tokens[start : i + 1]
            new = ["(", "("] + inner + [")", "/", "100", ")"]
            tokens = tokens[:start] + new + tokens[i + 2 :]
            i = start + len(new)
            continue
        i += 1

    return "".join(tokens)

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


def evaluate(expression: str) -> float:
    if not expression or not expression.strip():
        raise ValueError("Пустое выражение")
    expr = expression.strip().replace(",", ".")
    transformed = transform_percent_logic(expr)
    value = safe_compute(transformed)
    return round(value, 6)