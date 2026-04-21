import ply.lex as lex
import ply.yacc as yacc

# ======================
# TOKENS
# ======================

tokens = (
    "ID", "STRING", "NUMBER",
    "PLUS", "MINUS", "TIMES", "OVER",
    "ASSIGN_OP_WORD", "ASSIGN_OP_SIGN",
    "MAKE", "PRINT",
    "AMERICA_GREAT",
    "FACT", "LIE",
    "LPAREN", "RPAREN",
    "LBRACE", "RBRACE",
    "IF", "ELSE",
    "GE", "LE", "GT", "LT", "EQ",
    "AND", "OR",
    "QUESTION",
    "AS_LONG_AS"
)

t_LPAREN = r','
t_RPAREN = r';'
t_LBRACE = r':'
t_RBRACE = r'!'
t_ignore = ' \t.'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_ASSIGN_OP_SIGN = r'='
t_GT = r'>'
t_LT = r'<'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_OVER = r'/'
t_QUESTION = r'\?'

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
        'is': 'ASSIGN_OP_WORD',
        'are': 'ASSIGN_OP_WORD',
        'make': 'MAKE',
        'say': 'PRINT', 'tell': 'PRINT',
        'plus': 'PLUS',
        'minus': 'MINUS',
        'times': 'TIMES',
        'over': 'OVER',
        'fact': 'FACT',
        'lie': 'LIE',
        'if': 'IF',
        'else': 'ELSE',
        'and': 'AND',
        'or': 'OR',
    }
    t.type = keywords.get(val, 'ID')
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
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

# ======================
# PRECEDENCE
# ======================
# W PLY im niżej na liście, tym silniej wiąże operator.
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'QUESTION'),        # Pytajnik wiąże słabiej niż porównania...
    ('nonassoc', 'EQ', 'GE', 'LE', 'GT', 'LT', 'ASSIGN_OP_WORD'), # ...więc "is" wykona się najpierw.
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'OVER'),
)

# ======================
# PARSER
# ======================

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
                 | loop_statement"""
    p[0] = p[1]

# EXPRESSIONS
def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OVER expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = (p.slice[2].type, p[1], p[3])

def p_expression_comparison(p):
    """expression : expression EQ expression
                  | expression GE expression
                  | expression LE expression
                  | expression GT expression
                  | expression LT expression
                  | expression ASSIGN_OP_WORD expression"""
    # p[2] zwróci nam "is" lub "are", p.slice[2].type zwróci "ASSIGN_OP_WORD"
    p[0] = ('COMPARE', p.slice[2].type, p[1], p[3])

def p_expression_question(p):
    """expression : expression QUESTION"""
    p[0] = ('QUESTION', p[1])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_expression_value(p):
    """expression : NUMBER
                  | STRING
                  | ID
                  | FACT
                  | LIE"""
    if p.slice[1].type == 'FACT':
        p[0] = ('BOOL', True)
    elif p.slice[1].type == 'LIE':
        p[0] = ('BOOL', False)
    elif p.slice[1].type == 'ID':
        p[0] = ('VAR', p[1])
    else:
        p[0] = p[1]

# STATEMENTS
def p_assignment(p):
    """assignment : ID ASSIGN_OP_SIGN expression
                 | ID ASSIGN_OP_WORD expression
                 | MAKE ID expression"""
    if p.slice[1].type == 'MAKE':
        p[0] = ("assign", p[2], p[3])
    else:
        p[0] = ("assign", p[1], p[3])

def p_print(p):
    """print_statement : PRINT expression"""
    p[0] = ('print', p[2])

def p_if_statement(p):
    """if_statement : IF expression LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE LBRACE body RBRACE"""
    if len(p) == 6:
        p[0] = ('if', p[2], p[4])
    else:
        p[0] = ('if_else', p[2], p[4], p[8])

def p_loop_statement(p):
    """loop_statement : AS_LONG_AS expression LBRACE body RBRACE"""
    p[0] = ('while', p[2], p[4])

def p_error(p):
    if p:
        print(f"Syntax Error near '{p.value}' (line {p.lineno})")
    else:
        print("Syntax Error at EOF")

# ======================
# BUILD & TEST
# ======================

lexer = lex.lex()
parser = yacc.yacc()

import pprint

test_cases = [
    'x = 10 America is great.',
    'Make budget 1000 America is great.',
    'TheWall is "High" America is great.',
    'say "Believe me" America is great.',
    'say 2 + 2 * 2 America is great.',
    'say ,2 + 2; * 2 America is great.',
    'say fact is fact? America is great.',
    'say fact is fact? and lie is lie? America is great.',
    'say 10 plus 5 == 15? America is great.',
    'say fact or lie and lie America is great.',
    'if fact: say "It is true" ! America is great.',
    'if lie: say "Fake News" ! else: say "True Story"  if fact: say "I love" !! America is great.',
    'as long as x > 0: x = x - 1 ! America is great.',
    """
    make wall "test"
    america is "great"
    make wall_test wall is "test"?
    make america_test america is "great"?
    result is ,wall_test and america_test;
    as long as result==fact:
        say "Jestem w pętli"
        make result lie
    !
    say result
    America is great.
"""
]
#
if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    for i, code in enumerate(test_cases, 1):
        print(f"\n🚀 TEST #{i}:")
        print(f"KOD: {code.strip()[:100]}...")
        result = parser.parse(code)
        pp.pprint(result)