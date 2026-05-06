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



test_cases = [
    """
    make wall "high"
    if wall is high?:
        say wall!
    America is great.
    """,
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
