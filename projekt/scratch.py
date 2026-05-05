import ply.lex as lex
import ply.yacc as yacc
import pprint


tokens = (
    "ID",
    "STRING",
    "NUMBER",
    "PLUS",
    "MINUS",
    "TIMES",
    "OVER",
    "ASSIGN_OP_WORD",
    "ASSIGN_OP_SIGN",
    "MAKE",
    "PRINT",
    "AMERICA_GREAT",
    "FACT",
    "LIE",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "IF",
    "ELSE",
    "GE",
    "LE",
    "GT",
    "LT",
    "EQ",
    "AND",
    "OR",
    "QUESTION",
    "AS_LONG_AS",
    "BREAK",
    "NOT",
)
t_LPAREN = r","
t_RPAREN = r";"
t_LBRACE = r":"
t_RBRACE = r"!"
t_ignore = " \t"
t_GE = r">="
t_LE = r"<="
t_EQ = r"=="
t_ASSIGN_OP_SIGN = r"="
t_GT = r">"
t_LT = r"<"
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_OVER = r"/"
t_QUESTION = r"\?"
t_NOT = r"\~"

def t_AMERICA_GREAT(t):
    r"""America\s+is\s+great\."""
    return t

def t_AS_LONG_AS(t):
    r"""as\s+long\s+as"""
    return t

def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    val = t.value.lower()
    keywords = {
        "is": "ASSIGN_OP_WORD",
        "are": "ASSIGN_OP_WORD",
        "make": "MAKE",
        "say": "PRINT",
        "tell": "PRINT",
        "plus": "PLUS",
        "minus": "MINUS",
        "times": "TIMES",
        "over": "OVER",
        "fact": "FACT",
        "lie": "LIE",
        "if": "IF",
        "else": "ELSE",
        "and": "AND",
        "or": "OR",
        "stop": "BREAK",
    }
    t.type = keywords.get(val, "ID")
    return t

def t_STRING(t):
    r"""\"[^\"]*\""""
    return t

def t_NUMBER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t

def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


precedence = (
    ("left", "QUESTION"),
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("nonassoc", "EQ", "GE", "LE", "GT", "LT", "ASSIGN_OP_WORD"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "OVER"),
)


def p_program(p):
    """program : body AMERICA_GREAT
               | AMERICA_GREAT"""
    p[0] = [] if len(p) == 2 else p[1]

def p_body(p):
    """body : statement
            | body statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    """statement : assignment
                 | print_statement
                 | if_statement
                 | loop_statement
                 | BREAK"""
    if p.slice[1].type == "BREAK":
        p[0] = ("break",)
    else:
        p[0] = p[1]

def p_assignment(p):
    """assignment : ID ASSIGN_OP_SIGN expression
                  | ID ASSIGN_OP_WORD expression
                  | MAKE ID expression"""
    if p.slice[1].type == "MAKE":
        p[0] = ("assign", p[2], p[3])
    else:
        p[0] = ("assign", p[1], p[3])

def p_print_statement(p):
    """print_statement : PRINT expression"""
    p[0] = ("print", p[2])

def p_if_statement(p):
    """if_statement : IF expression LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE if_statement"""
    if len(p) == 6:
        p[0] = ("if", p[2], p[4])
    elif len(p) == 10:
        p[0] = ("if_else", p[2], p[4], p[8])
    else:
        p[0] = ("if_else_if", p[2], p[4], [p[7]])

def p_loop_statement(p):
    """loop_statement : AS_LONG_AS expression LBRACE body RBRACE"""
    p[0] = ("while", p[2], p[4])

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OVER expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = (p.slice[2].type, p[1], p[3])

def p_expression_compare(p):
    """expression : expression EQ expression
                  | expression GE expression
                  | expression LE expression
                  | expression GT expression
                  | expression LT expression
                  | expression ASSIGN_OP_WORD expression"""
    p[0] = ("COMPARE", p.slice[2].type, p[1], p[3])

def p_expression_unary(p):
    """expression : NOT expression"""
    p[0] = ("NOT", p[2])

def p_expression_question(p):
    """expression : expression QUESTION"""
    p[0] = ("QUESTION", p[1])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_expression_value(p):
    """expression : NUMBER
                  | STRING
                  | ID
                  | FACT
                  | LIE"""
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax Error near '{p.value}' (line {p.lineno})")
    else:
        print("Syntax Error at EOF")


lexer = lex.lex()
parser = yacc.yacc()


class SemanticError(Exception):
    """Niestandardowy wyjątek zgłaszany w przypadku błędów w logice TrumpScriptu."""
    pass

def infer_type(node, var_types):
    """Próbuje odgadnąć typ wyrażenia w czasie kompilacji."""
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
        if op == "PLUS":
            # PLUS może być matematyką (number) lub łączeniem tekstów (string)
            if infer_type(node[1], var_types) == "string":
                return "string"
            return "number"
        if op in ("MINUS", "TIMES", "OVER"):
            return "number"
    return "unknown"

def enforce_logical_condition(node, context_name, var_types):
    """Sprawdza, czy węzeł sprowadza się do wartości logicznej (fact/lie)."""
    node_type = infer_type(node, var_types)
    if node_type == "number":
        raise SemanticError(
            f"W {context_name} oczekiwano warunku logicznego (fact/lie), a podano liczbę lub wyrażenie arytmetyczne."
        )
    if node_type == "string":
        raise SemanticError(
            f"W {context_name} oczekiwano warunku logicznego (fact/lie), a podano tekst."
        )

def translate_to_python(node, indent=0, parent_prec=0, in_loop=False, var_types=None):
    if var_types is None:
        var_types = {}

    ind = "    " * indent

    if isinstance(node, list):
        if not node:
            return ind + "pass"
        return "\n".join(
            translate_to_python(stmt, indent, 0, in_loop, var_types) for stmt in node
        )

    if not isinstance(node, tuple):
        if node == "fact":
            return "True"
        if node == "lie":
            return "False"
        if (
            isinstance(node, str)
            and node not in ("True", "False")
            and not node.startswith('"')
        ):
            return node
        return str(node)

    op = node[0]

    # --- INSTRUKCJE ---
    if op == "assign":
        val_type = infer_type(node[2], var_types)
        var_types[node[1]] = val_type
        return (
            f"{ind}{node[1]} = {translate_to_python(node[2], 0, 0, in_loop, var_types)}"
        )

    elif op == "print":
        return f"{ind}print({translate_to_python(node[1], 0, 0, in_loop, var_types)})"

    elif op == "break":
        if not in_loop:
            raise SemanticError(
                "Instrukcja 'stop' (break) może być użyta TYLKO wewnątrz pętli 'as long as'."
            )
        return f"{ind}break"

    elif op == "while":
        enforce_logical_condition(node[1], "pętli 'as long as'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body = translate_to_python(node[2], indent + 1, 0, True, var_types)
        return f"{ind}while {cond}:\n{body}"

    elif op == "if":
        enforce_logical_condition(node[1], "instrukcji 'if'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body = translate_to_python(node[2], indent + 1, 0, in_loop, var_types)
        return f"{ind}if {cond}:\n{body}"

    elif op == "if_else":
        enforce_logical_condition(node[1], "instrukcji 'if-else'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body1 = translate_to_python(node[2], indent + 1, 0, in_loop, var_types)
        body2 = translate_to_python(node[3], indent + 1, 0, in_loop, var_types)
        return f"{ind}if {cond}:\n{body1}\n{ind}else:\n{body2}"

    elif op == "if_else_if":
        enforce_logical_condition(node[1], "instrukcji 'if-else-if'", var_types)
        cond = translate_to_python(node[1], 0, 0, in_loop, var_types)
        body = translate_to_python(node[2], indent + 1, 0, in_loop, var_types)
        else_body = translate_to_python(node[3], indent + 1, 0, in_loop, var_types)
        return f"{ind}if {cond}:\n{body}\n{ind}else:\n{else_body}"

    # --- WYRAŻENIA ---
    PRECEDENCE = {
        "OR": 1,
        "AND": 2,
        "NOT": 3,
        "COMPARE": 4,
        "PLUS": 5,
        "MINUS": 5,
        "TIMES": 6,
        "OVER": 6,
    }

    if op == "COMPARE":
        op_map = {
            "EQ": "==",
            "GE": ">=",
            "LE": "<=",
            "GT": ">",
            "LT": "<",
            "ASSIGN_OP_WORD": "==",
        }
        prec = PRECEDENCE["COMPARE"]
        left = translate_to_python(node[2], 0, prec, in_loop, var_types)
        right = translate_to_python(node[3], 0, prec + 1, in_loop, var_types)
        expr = f"{left} {op_map[node[1]]} {right}"
        return f"({expr})" if prec < parent_prec else expr

    elif op == "QUESTION":
        return translate_to_python(node[1], 0, parent_prec, in_loop, var_types)

    elif op == "NOT":
        enforce_logical_condition(node[1], "operatorze negacji (~)", var_types)
        prec = PRECEDENCE["NOT"]
        expr = f"not {translate_to_python(node[1], 0, prec, in_loop, var_types)}"
        return f"({expr})" if prec < parent_prec else expr

    # -------------------------------------------------------------
    # NOWE RESTRYKCJE: MATEMATYKA I TEKSTY
    # -------------------------------------------------------------
    elif op in ("PLUS", "MINUS", "TIMES", "OVER"):
        left_type = infer_type(node[1], var_types)
        right_type = infer_type(node[2], var_types)

        # 1. Zakaz wartości logicznych w działaniach
        if left_type == "bool" or right_type == "bool":
            raise SemanticError(
                f"Nie można używać 'fact' / 'lie' w operacjach matematycznych ('{op}')."
            )

        # 2. Zakaz mieszania typów (jeśli potrafimy je bezbłędnie zidentyfikować)
        if (
            left_type != "unknown"
            and right_type != "unknown"
            and left_type != right_type
        ):
            raise SemanticError(
                f"Nie można mieszać typów {left_type} oraz {right_type} w jednym działaniu ('{op}')."
            )

        # 3. Restrykcje dla tekstów (tylko łączenie przez PLUS)
        if left_type == "string" and op != "PLUS":
            raise SemanticError(
                f"Na tekstach (string) można używać tylko operacji 'plus'. Zakazana operacja: '{op}'."
            )

        # 4. Sprawdzenie dzielenia przez zero w czasie kompilacji (dla stałych 0)
        if op == "OVER" and node[2] == 0:
            raise SemanticError(
                "Błąd krytyczny: Dzielenie przez 0 jest absolutnie niedozwolone!"
            )

        op_map = {"PLUS": "+", "MINUS": "-", "TIMES": "*", "OVER": "/"}
        prec = PRECEDENCE[op]
        left = translate_to_python(node[1], 0, prec, in_loop, var_types)
        right = translate_to_python(node[2], 0, prec + 1, in_loop, var_types)
        expr = f"{left} {op_map[op]} {right}"
        return f"({expr})" if prec < parent_prec else expr

    elif op in ("AND", "OR"):
        enforce_logical_condition(node[1], f"operatorze '{op}'", var_types)
        enforce_logical_condition(node[2], f"operatorze '{op}'", var_types)
        op_map = {"AND": "and", "OR": "or"}
        prec = PRECEDENCE[op]
        left = translate_to_python(node[1], 0, prec, in_loop, var_types)
        right = translate_to_python(node[2], 0, prec + 1, in_loop, var_types)
        expr = f"{left} {op_map[op]} {right}"
        return f"({expr})" if prec < parent_prec else expr

    else:
        return f"UNKNOWN_NODE({node})"


test_cases = [
    "x = 10 America is great.",
    "Make budget 1000 America is great.",
    'TheWall is "High" America is great.',
    'say "Believe me" America is great.',
    "say 2 + 2 * 2 America is great.",
    "say ,2 + 2; * 2 America is great.",
    "say fact is fact? America is great.",
    "say fact is fact? and lie is lie? America is great.",
    "say 10 plus 5 == 15? America is great.",
    "say fact or lie and lie America is great.",
    'if fact: say "It is true" ! America is great.',
    'if lie: say "Fake News" ! else: say "True Story"  if fact: say "I love" !! America is great.',
    "as long as x > 0: x = x - 1 ! America is great.",
    """
    make wall "test"
    america is "great"
    make wall_test wall is "test"?
    make america_test america is "great"?
    result is ,wall_test and america_test;
    as long as result:
        say "Jestem w petli"
        make result lie
    !
    say result
    America is great.
    """,
    """make wall 100 
    if wall == 100: 
        say wall! 
    America is great.""",
]


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    for i, code in enumerate(test_cases, 1):
        print("=" * 60)
        print(f"TEST #{i}")
        print("=" * 60)
        print("KOD ŹRÓDŁOWY (TrumpScript):")
        print(code.strip())

        # Generowanie drzewa AST
        ast = parser.parse(code)

        print("\nDRZEWO SKŁADNIOWE (AST):")
        pp.pprint(ast)

        # Transpilacja AST do Pythona
        python_code = translate_to_python(ast)

        print("\nWYGENEROWANY KOD (Python):")
        print(python_code)
        print("\n")
