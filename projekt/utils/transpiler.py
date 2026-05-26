from .errors import SemanticError


PRECEDENCE = {
    "OR": 1, "AND": 2, "NOT": 3, "COMPARE": 4,
    "PLUS": 5, "MINUS": 5, "TIMES": 6, "OVER": 6,
}

OP_MAP_COMPARE = {
    "EQ": "==", "GE": ">=", "LE": "<=",
    "GT": ">", "LT": "<", "ASSIGN_OP_WORD": "==",
}

OP_MAP_MATH = {"PLUS": "+", "MINUS": "-", "TIMES": "*", "OVER": "//"}

OP_MAP_LOGIC = {"AND": "and", "OR": "or"}


def _semantic_error(line, msg):
    """Tworzy SemanticError z prefiksem numeru linii, jeśli jest dostępny."""
    if line is None:
        return SemanticError(msg)
    return SemanticError(f"Linia {line}: {msg}")


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
            t1 = infer_type(node[1], var_types)
            t2 = infer_type(node[2], var_types)
            # Konkatenacja stringów dla PLUS pozostaje stringiem
            if op == "PLUS" and t1 == "string" and t2 == "string":
                return "string"
            return "number"

    return "unknown"


def compute_value(node, var_values):
    """Wylicza wartość wyrażenia w czasie kompilacji, jeśli jest deterministyczna.

    Zwraca int, str (bez cudzysłowów) albo None, gdy wartość nie jest znana
    statycznie. Używane między innymi do wykrywania dzielenia przez zero,
    nawet gdy mianownikiem jest zmienna o znanej wartości 0.
    """
    if isinstance(node, int):
        return node
    if isinstance(node, str):
        if len(node) >= 2 and node.startswith('"') and node.endswith('"'):
            return node[1:-1]
        if node in ("fact", "lie"):
            return None
        return var_values.get(node)

    if isinstance(node, tuple):
        op = node[0]
        if op in ("PLUS", "MINUS", "TIMES", "OVER"):
            v1 = compute_value(node[1], var_values)
            v2 = compute_value(node[2], var_values)
            if v1 is None or v2 is None:
                return None
            if op == "PLUS":
                if isinstance(v1, int) and isinstance(v2, int):
                    return v1 + v2
                if isinstance(v1, str) and isinstance(v2, str):
                    return v1 + v2
                return None
            if not (isinstance(v1, int) and isinstance(v2, int)):
                return None
            if op == "MINUS":
                return v1 - v2
            if op == "TIMES":
                return v1 * v2
            if op == "OVER":
                if v2 == 0:
                    return None
                return v1 / v2
    return None


def collect_assigned_vars(node):
    """Zbiera nazwy zmiennych przypisanych w danym poddrzewie AST."""
    if isinstance(node, list):
        names = set()
        for item in node:
            names.update(collect_assigned_vars(item))
        return names
    if isinstance(node, tuple):
        if node[0] == "assign":
            names = {node[1]}
            names.update(collect_assigned_vars(node[2]))
            return names
        names = set()
        for sub in node[1:]:
            names.update(collect_assigned_vars(sub))
        return names
    return set()


def enforce_logical_condition(node, context_name, var_types, current_line):
    """Wymusza, aby wyrażenie było typem boolowskim (fact/lie lub porównanie)."""
    node_type = infer_type(node, var_types)
    if node_type == "number":
        raise _semantic_error(
            current_line,
            f"W {context_name} oczekiwano warunku logicznego, a podano liczbę (typ 'number').",
        )
    if node_type == "string":
        raise _semantic_error(
            current_line,
            f"W {context_name} oczekiwano warunku logicznego, a podano tekst (typ 'string').",
        )


def _wrap_if_needed(expr, prec, parent_prec):
    """Owija wyrażenie w nawiasy jeśli priorytet jest niższy niż nadrzędny."""
    return f"({expr})" if prec < parent_prec else expr


def translate_to_python(node, indent=0, parent_prec=0, in_loop=False,
                        var_types=None, var_values=None, current_line=None):
    if var_types is None:
        var_types = {}
    if var_values is None:
        var_values = {}

    ind = "    " * indent

    # --- LISTA INSTRUKCJI ---
    if isinstance(node, list):
        return (ind + "pass") if not node else "\n".join(
            translate_to_python(s, indent, 0, in_loop, var_types, var_values, current_line)
            for s in node
        )

    # --- WĘZŁY ATOMOWE ---
    if not isinstance(node, tuple):
        if node == "fact":   return "True"
        if node == "lie":    return "False"
        if isinstance(node, str) and not node.startswith('"'):
            if node not in var_types and node not in ("fact", "lie"):
                raise _semantic_error(
                    current_line,
                    f"Zmienna '{node}' nie została zadeklarowana przed użyciem!",
                )
            return node
        return str(node)

    op = node[0]

    # --- INSTRUKCJE (każda niesie własny numer linii w ostatnim polu) ---
    if op == "assign":
        # ("assign", name, expr, lineno)
        stmt_line = node[3]
        # Najpierw tłumaczymy prawą stronę, by błędy semantyczne w wyrażeniu
        # zostały podniesione zanim zaktualizujemy typ/wartość zmiennej.
        val = translate_to_python(node[2], 0, 0, in_loop, var_types, var_values, stmt_line)
        new_type = infer_type(node[2], var_types)
        new_value = compute_value(node[2], var_values)
        var_types[node[1]] = new_type
        if new_value is not None:
            var_values[node[1]] = new_value
        else:
            var_values.pop(node[1], None)
        return f"{ind}{node[1]} = {val}"

    if op == "print":
        # ("print", expr, lineno)
        stmt_line = node[2]
        val = translate_to_python(node[1], 0, 0, in_loop, var_types, var_values, stmt_line)
        return f"{ind}print({val})"

    if op == "break":
        # ("break", lineno)
        stmt_line = node[1]
        if not in_loop:
            raise _semantic_error(
                stmt_line,
                "'stop' może być użyte TYLKO wewnątrz pętli 'as long as'.",
            )
        return f"{ind}break"

    if op == "while":
        # ("while", cond, body, lineno)
        stmt_line = node[3]
        enforce_logical_condition(node[1], "pętli 'as long as'", var_types, stmt_line)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types, var_values, stmt_line)
        body = translate_to_python(node[2], indent + 1, 0, True, var_types, var_values, stmt_line)
        # Po pętli wartości zmiennych modyfikowanych w ciele są nieznane statycznie.
        for v in collect_assigned_vars(node[2]):
            var_values.pop(v, None)
        return f"{ind}while {cond}:\n{body}"

    if op == "if":
        # ("if", cond, body, lineno)
        stmt_line = node[3]
        enforce_logical_condition(node[1], "instrukcji 'if'", var_types, stmt_line)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types, var_values, stmt_line)
        body = translate_to_python(node[2], indent + 1, 0, in_loop, var_types, var_values, stmt_line)
        for v in collect_assigned_vars(node[2]):
            var_values.pop(v, None)
        return f"{ind}if {cond}:\n{body}"

    if op == "if_else":
        # ("if_else", cond, body1, body2, lineno)
        stmt_line = node[4]
        enforce_logical_condition(node[1], "instrukcji 'if-else'", var_types, stmt_line)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types, var_values, stmt_line)
        snapshot = dict(var_values)
        body1 = translate_to_python(node[2], indent + 1, 0, in_loop, var_types, var_values, stmt_line)
        var_values.clear()
        var_values.update(snapshot)
        body2 = translate_to_python(node[3], indent + 1, 0, in_loop, var_types, var_values, stmt_line)
        for v in collect_assigned_vars(node[2]) | collect_assigned_vars(node[3]):
            var_values.pop(v, None)
        return f"{ind}if {cond}:\n{body1}\n{ind}else:\n{body2}"

    if op == "if_else_if":
        # ("if_else_if", cond, body, else_branch, lineno)
        stmt_line = node[4]
        enforce_logical_condition(node[1], "instrukcji 'if-else-if'", var_types, stmt_line)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types, var_values, stmt_line)
        snapshot = dict(var_values)
        body = translate_to_python(node[2], indent + 1, 0, in_loop, var_types, var_values, stmt_line)
        var_values.clear()
        var_values.update(snapshot)
        else_body = translate_to_python(node[3], indent + 1, 0, in_loop, var_types, var_values, stmt_line)
        for v in collect_assigned_vars(node[2]) | collect_assigned_vars(node[3]):
            var_values.pop(v, None)
        return f"{ind}if {cond}:\n{body}\n{ind}else:\n{else_body}"

    # --- WYRAŻENIA (linię dziedziczą po nadrzędnej instrukcji) ---
    if op == "COMPARE":
        left_type = infer_type(node[2], var_types)
        right_type = infer_type(node[3], var_types)

        if left_type != "unknown" and right_type != "unknown" and left_type != right_type:
            raise _semantic_error(
                current_line,
                f"Błąd typów w porównaniu: nie można porównywać typu '{left_type}' "
                f"z typem '{right_type}'!",
            )

        prec = PRECEDENCE["COMPARE"]
        left = translate_to_python(node[2], 0, prec, in_loop, var_types, var_values, current_line)
        right = translate_to_python(node[3], 0, prec + 1, in_loop, var_types, var_values, current_line)
        return _wrap_if_needed(
            f"{left} {OP_MAP_COMPARE[node[1]]} {right}", prec, parent_prec
        )

    if op == "QUESTION":
        return translate_to_python(node[1], 0, parent_prec, in_loop, var_types, var_values, current_line)

    if op == "NOT":
        enforce_logical_condition(node[1], "operatorze negacji (~)", var_types, current_line)
        prec = PRECEDENCE["NOT"]
        inner = translate_to_python(node[1], 0, prec, in_loop, var_types, var_values, current_line)
        return _wrap_if_needed(f"not {inner}", prec, parent_prec)

    if op in OP_MAP_MATH:
        left_type = infer_type(node[1], var_types)
        right_type = infer_type(node[2], var_types)

        # Wartości logiczne nie biorą udziału w arytmetyce.
        if left_type == "bool" or right_type == "bool":
            raise _semantic_error(
                current_line,
                f"Nie można używać typów logicznych (fact/lie) w operacji '{op}'.",
            )

        # Operacje arytmetyczne tylko na tych samych typach.
        if left_type != "unknown" and right_type != "unknown" and left_type != right_type:
            raise _semantic_error(
                current_line,
                f"Błąd typów w operacji '{op}': nie można łączyć typu '{left_type}' "
                f"z typem '{right_type}'. Operacje arytmetyczne wymagają zgodności typów.",
            )

        # Na tekstach dozwolone jest wyłącznie 'plus' (konkatenacja).
        if (left_type == "string" or right_type == "string") and op != "PLUS":
            raise _semantic_error(
                current_line,
                f"Na tekstach można używać tylko 'plus'. Zakazana operacja: '{op}'.",
            )

        # Wykrywanie dzielenia przez 0 — także gdy dzielnikiem jest zmienna
        # o znanej (statycznie wywnioskowanej) wartości 0.
        if op == "OVER":
            right_val = compute_value(node[2], var_values)
            if isinstance(right_val, (int, float)) and right_val == 0:
                raise _semantic_error(
                    current_line,
                    "Dzielenie przez 0 jest niedozwolone "
                    "(wykryto wartość 0 w mianowniku).",
                )

        prec = PRECEDENCE[op]
        left = translate_to_python(node[1], 0, prec, in_loop, var_types, var_values, current_line)
        right = translate_to_python(node[2], 0, prec + 1, in_loop, var_types, var_values, current_line)
        return _wrap_if_needed(
            f"{left} {OP_MAP_MATH[op]} {right}", prec, parent_prec
        )

    if op in OP_MAP_LOGIC:
        enforce_logical_condition(node[1], f"operatorze '{op}'", var_types, current_line)
        enforce_logical_condition(node[2], f"operatorze '{op}'", var_types, current_line)
        prec = PRECEDENCE[op]
        left = translate_to_python(node[1], 0, prec, in_loop, var_types, var_values, current_line)
        right = translate_to_python(node[2], 0, prec + 1, in_loop, var_types, var_values, current_line)
        return _wrap_if_needed(
            f"{left} {OP_MAP_LOGIC[op]} {right}", prec, parent_prec
        )

    return f"UNKNOWN_NODE({node})"
