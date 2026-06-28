from itertools import product
from sympy import sympify
from sympy.logic.boolalg import BooleanFunction
from pathlib import Path
import re

I18 = {"ES": {"True": "V", "False": "F"}, "EN": {"True": "T", "False": "F"}}
LANGUAGE = "ES"


def normalize(expression: str) -> str:
    """Convert Unicode logic symbols to sympy-compatible syntax."""
    expression = re.sub(
        r"(.+?)\s*↔\s*(.+)",
        lambda m: f"Equivalent({m.group(1)}, {m.group(2)})",
        expression,
    )

    expression = re.sub(
        r"(.+?)\s*<->\s*(.+)",
        lambda m: f"Equivalent({m.group(1)}, {m.group(2)})",
        expression,
    )

    return (
        expression.replace("¬", "~")
        .replace("→", ">>")
        .replace("->", ">>")
        .replace("∧", "&")
        .replace("∨", "|")
    )


def pretty(expr, parent=None):
    from sympy.logic.boolalg import Implies, And, Or, Not, Equivalent

    if expr.is_Symbol:
        return str(expr)
    elif isinstance(expr, Not):
        inner = pretty(expr.args[0], parent=Not)
        return f"¬{inner}"
    elif isinstance(expr, Equivalent):
        a, b = expr.args
        inner = f"{pretty(a, parent=Equivalent)} ↔ {pretty(b, parent=Equivalent)}"
        if parent in (And, Or, Not, Implies):
            return f"({inner})"
        return inner
    elif isinstance(expr, And):
        result = " ∧ ".join(sorted(pretty(a, parent=And) for a in expr.args))
        if parent in (Or, Implies):
            return f"({result})"
        return result
    elif isinstance(expr, Or):
        result = " ∨ ".join(sorted(pretty(a, parent=Or) for a in expr.args))
        if parent in (And, Implies):
            return f"({result})"
        return result
    elif isinstance(expr, Implies):
        a, b = expr.args
        left = pretty(a, parent=Implies)
        right = pretty(b, parent=Implies)
        if isinstance(b, Implies):
            right = f"({right})"
        inner = f"{left} → {right}"
        if parent in (And, Or, Not):
            return f"({inner})"
        return inner
    else:
        return str(expr)


def truth_table_markdown(expression: str) -> str:
    expr = sympify(normalize(expression))

    variables = sorted(expr.free_symbols, key=lambda s: s.name)

    subexpressions = []

    def visit(node):
        for arg in getattr(node, "args", ()):
            visit(arg)
        if isinstance(node, BooleanFunction) and node not in subexpressions:
            subexpressions.append(node)

    visit(expr)

    headers = [str(v) for v in variables] + [pretty(s) for s in subexpressions]

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for values in product([True, False], repeat=len(variables)):
        TVALUE = I18[LANGUAGE]["True"]
        FVALUE = I18[LANGUAGE]["False"]
        env = dict(zip(variables, values))
        row = [TVALUE if v else FVALUE for v in values]
        for subexpr in subexpressions:
            result = bool(subexpr.subs(env))
            row.append(TVALUE if result else FVALUE)
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def truth_table_csv(expression: str) -> str:
    expr = sympify(normalize(expression))

    variables = sorted(expr.free_symbols, key=lambda s: s.name)

    subexpressions = []

    def visit(node):
        for arg in getattr(node, "args", ()):
            visit(arg)
        if isinstance(node, BooleanFunction) and node not in subexpressions:
            subexpressions.append(node)

    visit(expr)

    headers = [str(v) for v in variables] + [pretty(s) for s in subexpressions]
    lines = ["|".join(headers)]

    for values in product([True, False], repeat=len(variables)):
        TVALUE = I18[LANGUAGE]["True"]
        FVALUE = I18[LANGUAGE]["False"]
        env = dict(zip(variables, values))
        row = [TVALUE if v else FVALUE for v in values]
        for subexpr in subexpressions:
            result = bool(subexpr.subs(env))
            row.append(TVALUE if result else FVALUE)
        lines.append("|".join(row))

    return "\n".join(lines)


def compute_truth_table(expression: str):
    expr = sympify(normalize(expression))
    variables = sorted(expr.free_symbols, key=lambda s: s.name)

    subexpressions = []

    def visit(node):
        for arg in getattr(node, "args", ()):
            visit(arg)
        if isinstance(node, BooleanFunction) and node not in subexpressions:
            subexpressions.append(node)

    visit(expr)

    headers = [str(v) for v in variables] + [pretty(s) for s in subexpressions]
    rows = []

    for values in product([True, False], repeat=len(variables)):
        TVALUE = I18[LANGUAGE]["True"]
        FVALUE = I18[LANGUAGE]["False"]
        env = dict(zip(variables, values))
        row = [TVALUE if v else FVALUE for v in values]
        for subexpr in subexpressions:
            result = bool(subexpr.subs(env))
            row.append(TVALUE if result else FVALUE)
        rows.append(row)

    return {"headers": headers, "rows": rows}


def evaluate(expresions, format="md"):
    result_file_name = "./result.md"
    Path(result_file_name).unlink(missing_ok=True)

    for e in expresions:
        if format == "md":
            result = truth_table_markdown(e)
        else:
            result = truth_table_csv(e)

        print(f"Solved {e}")

        with open(result_file_name, "a") as file:
            file.write(f"# {e}\n")
            file.write(result)
            file.write("\n\n-----------------\n")


# fmt: off
expresions = [
    "(p → q) ∧ (¬r ∨ q)",
    "(q → p) ∧ (r ∨ p)",
    "¬(p ∨ ¬q) → (¬r ∧ p)",
    "(¬p ∧ q) → (r ∧ p)",


    # "¬(p → q) ∨ (q ∨ r)",
    # "(p ∧ ¬q) ∨ (q ∨ r)",
    # "(p ∨ ¬q) ∨ (q ∨ r)",
    # "(p ∧ q) ∧ r",
    # "(¬p ∧ q) ∨ (q ∨ r)",
    # "¬p ∧ (q ∨ r)",
    # "p -> q",
    # "p <-> q",
    # "(p∨¬q)→(¬p∧q)",
    # "((p & q) | (p & r)) >> t",
    # "(p & q) >> r",
    # "((p | q) & ~r) >> s",
    # "(((p & q) | (r & ~s)) >> (t | u)) & ((p >> r) | (q >> s))",

]
# fmt: on

if __name__ == "__main__":
    evaluate(expresions, "csv")
