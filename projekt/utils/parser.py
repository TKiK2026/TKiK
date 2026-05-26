import ply.yacc as yacc
from .lexer import tokens, lexer
from .errors import ParserError
precedence = (
    ("left",    "QUESTION"),
    ("left",    "OR"),
    ("left",    "AND"),
    ("right",   "NOT"),
    ("nonassoc","EQ", "GE", "LE", "GT", "LT", "ASSIGN_OP_WORD"),
    ("left",    "PLUS", "MINUS"),
    ("left",    "TIMES", "OVER"),
)

def p_program(p):
    """program : body AMERICA_GREAT
               | AMERICA_GREAT"""
    p[0] = [] if len(p) == 2 else p[1]

def p_body(p):
    """body : statement
            | body statement"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_statement(p):
    """statement : assignment
                 | print_statement
                 | if_statement
                 | loop_statement
                 | BREAK"""
    if p.slice[1].type == "BREAK":
        p[0] = ("break", p.lineno(1))
    else:
        p[0] = p[1]

def p_assignment(p):
    """assignment : ID ASSIGN_OP_SIGN expression
                  | ID ASSIGN_OP_WORD expression
                  | MAKE ID expression"""
    line = p.lineno(1)
    if p.slice[1].type == "MAKE":
        p[0] = ("assign", p[2], p[3], line)
    else:
        p[0] = ("assign", p[1], p[3], line)

def p_print_statement(p):
    """print_statement : PRINT expression"""
    p[0] = ("print", p[2], p.lineno(1))

def p_if_statement(p):
    """if_statement : IF expression LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE if_statement"""
    line = p.lineno(1)
    if len(p) == 6:
        p[0] = ("if", p[2], p[4], line)
    elif len(p) == 10:
        p[0] = ("if_else", p[2], p[4], p[8], line)
    else:
        p[0] = ("if_else_if", p[2], p[4], [p[7]], line)

def p_loop_statement(p):
    """loop_statement : AS_LONG_AS expression LBRACE body RBRACE"""
    p[0] = ("while", p[2], p[4], p.lineno(1))

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
        raise ParserError(f"Linia {p.lineno}: błąd składniowy w pobliżu '{p.value}'.")
    else:
        last_line = lexer.lineno
        raise ParserError(
            f"Linia {last_line}: błąd składniowy — niespodziewany koniec kodu (EOF)."
        )

parser = yacc.yacc()


def parse_code(code):
    """Parsuje kod TrumpScript, resetując numerację linii lexera do 1.

    Lexer PLY jest singletonem modułowym i jego `lineno` nie zeruje się
    samoczynnie między kolejnymi wywołaniami `parser.parse`, przez co
    numery linii w komunikatach o błędach kumulowałyby się przy każdej
    translacji. Ta funkcja gwarantuje, że każde tłumaczenie startuje
    z linią 1.
    """
    lexer.lineno = 1
    return parser.parse(code, lexer=lexer)
