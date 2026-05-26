import ply.lex as lex
from .errors import LexerError
tokens = (
    "ID", "STRING", "NUMBER",
    "PLUS", "MINUS", "TIMES", "OVER",
    "ASSIGN_OP_WORD", "ASSIGN_OP_SIGN",
    "MAKE", "PRINT",
    "AMERICA_GREAT",
    "FACT", "LIE",
    "LPAREN", "RPAREN", "LBRACE", "RBRACE",
    "IF", "ELSE",
    "GE", "LE", "GT", "LT", "EQ",
    "AND", "OR",
    "QUESTION", "AS_LONG_AS", "BREAK", "NOT",
)

t_LPAREN       = r","
t_RPAREN       = r";"
t_LBRACE       = r":"
t_RBRACE       = r"!"
t_ignore       = " \t"
t_GE           = r">="
t_LE           = r"<="
t_EQ           = r"=="
t_ASSIGN_OP_SIGN = r"="
t_GT           = r">"
t_LT           = r"<"
t_PLUS         = r"\+"
t_MINUS        = r"-"
t_TIMES        = r"\*"
t_OVER         = r"/"
t_QUESTION     = r"\?"
t_NOT          = r"\~"

KEYWORDS = {
    "is":    "ASSIGN_OP_WORD",
    "are":   "ASSIGN_OP_WORD",
    "make":  "MAKE",
    "say":   "PRINT",
    "tell":  "PRINT",
    "plus":  "PLUS",
    "minus": "MINUS",
    "times": "TIMES",
    "over":  "OVER",
    "fact":  "FACT",
    "lie":   "LIE",
    "if":    "IF",
    "else":  "ELSE",
    "and":   "AND",
    "or":    "OR",
    "stop":  "BREAK",
}

def t_AMERICA_GREAT(t):
    r"""America\s+is\s+great\."""
    return t

def t_AS_LONG_AS(t):
    r"""as\s+long\s+as"""
    return t

def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    t.type = KEYWORDS.get(t.value.lower(), "ID")
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
    raise LexerError(f"Linia {t.lexer.lineno}: nielegalny znak '{t.value[0]}'.")

lexer = lex.lex()