from .errors import SemanticError

PRECEDENCE = {
    "OR": 1, "AND": 2, "NOT": 3, "COMPARE": 4,
    "PLUS": 5, "MINUS": 5, "TIMES": 6, "OVER": 6,
}

OP_MAP_COMPARE = {
    "EQ": "==", "GE": ">=", "LE": "<=",
    "GT": ">", "LT": "<", "ASSIGN_OP_WORD": "==",
}

OP_MAP_MATH = {"PLUS": "+", "MINUS": "-", "TIMES": "*", "OVER": "/"}
OP_MAP_LOGIC = {"AND": "and", "OR": "or"}


def infer_type(node, var_types):
    """Zgaduje typ wyrażenia na podstawie AST i aktualnych zmiennych."""
    if isinstance(node, int):
        return "number"
    if node in ("fact", "lie"):
        return "bool"
    if isinstance(node, str) and node.startswith('"'):
        return "string"
    if isinstance(node, str):
        return var_types.get(node, "unknown")

    if isinstance(node, tuple):
        op = node[0]
        if op in ("COMPARE", "AND", "OR", "NOT", "QUESTION"):
            return "bool"
        if op in ("PLUS", "MINUS", "TIMES", "OVER"):
            # Jeśli w dodawaniu jest string, wynik to string (konkatenacja)
            if op == "PLUS":
                t1 = infer_type(node[1], var_types)
                t2 = infer_type(node[2], var_types)
                if t1 == "string" or t2 == "string":
                    return "string"
            return "number"

    return "unknown"


def enforce_logical_condition(node, context_name, var_types):
    """Wymusza, aby wyrażenie było typem boolowskim (fact/lie lub porówanie)."""
    node_type = infer_type(node, var_types)
    if node_type == "number":
        raise SemanticError(
            f"W {context_name} oczekiwano warunku logicznego, a podano liczbę (typ 'number')."
        )
    if node_type == "string":
        raise SemanticError(
            f"W {context_name} oczekiwano warunku logicznego, a podano tekst (typ 'string')."
        )


def _wrap_if_needed(expr, prec, parent_prec):
    """Owija wyrażenie w nawiasy jeśli priorytet jest niższy niż nadrzędny."""
    return f"({expr})" if prec < parent_prec else expr


def translate_to_python(node, indent=0, parent_prec=0, in_loop=False, var_types=None):
    if var_types is None:
        var_types = {}

    ind = "    " * indent

    # --- LISTA INSTRUKCJI ---
    if isinstance(node, list):
        return (ind + "pass") if not node else "\n".join(
            translate_to_python(s, indent, 0, in_loop, var_types) for s in node
        )

    # --- WĘZŁY ATOMOWE ---
    if not isinstance(node, tuple):
        if node == "fact":   return "True"
        if node == "lie":    return "False"
        if isinstance(node, str) and not node.startswith('"'):
            # Sprawdzenie czy zmienna istnieje przed użyciem (zapobiega runtime errorom)
            if node not in var_types and node not in ("fact", "lie"):
                raise SemanticError(f"Zmienna '{node}' nie została zadeklarowana przed użyciem!")
            return node
        return str(node)

    op = node[0]

    # --- INSTRUKCJE ---
    if op == "assign":
        # Rejestrujemy typ zmiennej w słowniku środowiska
        var_types[node[1]] = infer_type(node[2], var_types)
        val = translate_to_python(node[2], 0, 0, in_loop, var_types)
        return f"{ind}{node[1]} = {val}"

    if op == "print":
        val = translate_to_python(node[1], 0, 0, in_loop, var_types)
        return f"{ind}print({val})"

    if op == "break":
        if not in_loop:
            raise SemanticError("'stop' może być użyte TYLKO wewnątrz pętli 'as long as'.")
        return f"{ind}break"

    if op == "while":
        enforce_logical_condition(node[1], "pętli 'as long as'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body = translate_to_python(node[2], indent + 1, 0, True, var_types)
        return f"{ind}while {cond}:\n{body}"

    if op == "if":
        enforce_logical_condition(node[1], "instrukcji 'if'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body = translate_to_python(node[2], indent + 1, 0, in_loop, var_types)
        return f"{ind}if {cond}:\n{body}"

    if op == "if_else":
        enforce_logical_condition(node[1], "instrukcji 'if-else'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body1 = translate_to_python(node[2], indent + 1, 0, in_loop, var_types)
        body2 = translate_to_python(node[3], indent + 1, 0, in_loop, var_types)
        return f"{ind}if {cond}:\n{body1}\n{ind}else:\n{body2}"

    if op == "if_else_if":
        enforce_logical_condition(node[1], "instrukcji 'if-else-if'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body = translate_to_python(node[2], indent + 1, 0, in_loop, var_types)
        else_body = translate_to_python(node[3], indent + 1, 0, in_loop, var_types)
        return f"{ind}if {cond}:\n{body}\n{ind}else:\n{else_body}"

    # --- WYRAŻENIA ---
    if op == "COMPARE":
        # 1. Pobieramy oczekiwane typy obu stron porównania
        left_type = infer_type(node[2], var_types)
        right_type = infer_type(node[3], var_types)

        # 2. Sprawdzamy, czy typy są znane i czy się od siebie różnią
        if left_type != "unknown" and right_type != "unknown" and left_type != right_type:
            raise SemanticError(
                f"Błąd typów w porównaniu: Nie można porównywać typu '{left_type}' "
                f"z typem '{right_type}'!"
            )

        # 3. Jeśli typy są zgodne, generujemy kod Pythona (tak jak dotychczas)
        prec = PRECEDENCE["COMPARE"]
        left = translate_to_python(node[2], 0, prec, in_loop, var_types)
        right = translate_to_python(node[3], 0, prec + 1, in_loop, var_types)
        return _wrap_if_needed(f"{left} {OP_MAP_COMPARE[node[1]]} {right}", prec, parent_prec)

    if op == "QUESTION":
        return translate_to_python(node[1], 0, parent_prec, in_loop, var_types)

    if op == "NOT":
        enforce_logical_condition(node[1], "operatorze negacji (~)", var_types)
        prec = PRECEDENCE["NOT"]
        inner = translate_to_python(node[1], 0, prec, in_loop, var_types)
        return _wrap_if_needed(f"not {inner}", prec, parent_prec)

    if op in OP_MAP_MATH:
        left_type = infer_type(node[1], var_types)
        right_type = infer_type(node[2], var_types)

        # Ręczne wymuszanie typów dla działań matematycznych
        if left_type == "bool" or right_type == "bool":
            raise SemanticError(f"Nie można używać typów logicznych (fact/lie) w operacjach '{op}'.")

        if left_type == "string" or right_type == "string":
            if op != "PLUS":
                raise SemanticError(f"Na tekstach można używać tylko 'plus'. Zakazana operacja: '{op}'.")

        if op == "OVER" and node[2] == 0:
            raise SemanticError("Dzielenie przez 0 jest niedozwolone w czasie kompilacji!")

        prec = PRECEDENCE[op]
        left = translate_to_python(node[1], 0, prec, in_loop, var_types)
        right = translate_to_python(node[2], 0, prec + 1, in_loop, var_types)
        return _wrap_if_needed(f"{left} {OP_MAP_MATH[op]} {right}", prec, parent_prec)

    if op in OP_MAP_LOGIC:
        enforce_logical_condition(node[1], f"operatorze '{op}'", var_types)
        enforce_logical_condition(node[2], f"operatorze '{op}'", var_types)
        prec = PRECEDENCE[op]
        left = translate_to_python(node[1], 0, prec, in_loop, var_types)
        right = translate_to_python(node[2], 0, prec + 1, in_loop, var_types)
        return _wrap_if_needed(f"{left} {OP_MAP_LOGIC[op]} {right}", prec, parent_prec)

    return f"UNKNOWN_NODE({node})"