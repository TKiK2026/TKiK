import re
import sys
import ply.lex as lex
import ply.yacc as yacc

# ==========================================================
# 1. LEXER
# ==========================================================

tokens = (
    'PRINT',
    'NUMBER', 'STRING',
    'ID',
    'IS', 'ARE', 'MAKE',
    'TRUE', 'FALSE',
    'END_PROG',
    'PLUS', 'MINUS', 'TIMES', 'OVER',
    'LT', 'GT',
    'NOT', 'AND', 'OR',
    'IF', 'ELSE_IF', 'ELSE',
    'AS_LONG_AS',
    'QUESTION',
    'COLON', 'EXCLAIM',
)

# Przecinki i średniki są IGNOROWANE (ozdobniki składni)
t_ignore = ' \t'

# ------- Wielosłowne tokeny NAJPIERW (kolejność ma znaczenie w PLY) -------

def t_END_PROG(t):
    r'America\s+is\s+great'
    return t

def t_ELSE_IF(t):
    r'else\s+if'
    return t

def t_AS_LONG_AS(t):
    r'as\s+long\s+as'
    return t

# ------- Pojedyncze znaki -------

def t_PLUS(t):
    r'\+'
    return t

def t_MINUS(t):
    r'-'
    return t

def t_TIMES(t):
    r'\*'
    return t

def t_OVER(t):
    r'/'
    return t

def t_LT(t):
    r'<'
    return t

def t_GT(t):
    r'>'
    return t

def t_QUESTION(t):
    r'\?'
    return t

def t_COLON(t):
    r':'
    return t

def t_EXCLAIM(t):
    r'!'
    return t

# Przecinki i średniki ignorowane - są ozdobnikami składni
def t_ignore_separators(t):
    r'[,;]'
    pass

# ------- Liczby i stringi -------

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    if t.value < 1000000:
        print(f"BLAD: {t.value} to grosze! Musi byc >= 1mln.")
        sys.exit()
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

# ------- Identyfikatory i słowa kluczowe -------

# Słowa ignorowane przez parser (ozdobniki retoryczne)
FILLER_WORDS = {
    'the', 'a', 'an', 'of', 'to', 'in', 'that', 'it', 'with',
    'at', 'by', 'for', 'on', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'very', 'really',
    'totally', 'absolutely', 'bigly', 'huge', 'tremendous',
    'fantastic', 'amazing', 'wonderful', 'beautiful', 'strong',
    'smart', 'badly', 'good', 'bad', 'many', 'much', 'so', 'such',
    'all', 'just', 'now', 'then', 'some', 'any', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'between',
    'out', 'off', 'down', 'up', 'again', 'further', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'same',
    'own', 'too', 'only', 'also', 'about', 'against', 'while',
    'because', 'until', 'since', 'under', 'over',
}

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    val = t.value.lower()

    if val in ('tell', 'say'):               t.type = 'PRINT'
    elif val == 'is':                         t.type = 'IS'
    elif val == 'are':                        t.type = 'ARE'
    elif val == 'make':                       t.type = 'MAKE'
    elif val == 'fact':                       t.type = 'TRUE'
    elif val == 'lie':                        t.type = 'FALSE'
    elif val == 'plus':                       t.type = 'PLUS'
    elif val == 'minus':                      t.type = 'MINUS'
    elif val == 'times':                      t.type = 'TIMES'
    elif val == 'over':                       t.type = 'OVER'
    elif val in ('less', 'fewer', 'smaller'): t.type = 'LT'
    elif val in ('greater', 'larger'):        t.type = 'GT'
    elif val == 'not':                        t.type = 'NOT'
    elif val == 'and':                        t.type = 'AND'
    elif val == 'or':                         t.type = 'OR'
    elif val == 'if':                         t.type = 'IF'
    elif val == 'else':                       t.type = 'ELSE'
    elif val in FILLER_WORDS:
        return None  # ignoruj słowa ozdobne

    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Niedozwolony znak: '{t.value[0]}' w linii {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex(reflags=re.IGNORECASE)

# ==========================================================
# 2. PARSER
# ==========================================================

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'OVER'),
)

# ---------- Program ----------

def p_program(p):
    'program : statements END_PROG'
    p[0] = p[1]

# ---------- Statements ----------

def p_statements_multiple(p):
    'statements : statements statement'
    p[0] = p[1] + "\n" + p[2]

def p_statements_single(p):
    'statements : statement'
    p[0] = p[1]

# Przypisanie: X is/are Y
def p_statement_assign_is(p):
    '''statement : ID IS expression
                 | ID ARE expression'''
    p[0] = f"{p[1]} = {p[3]}"

# Przypisanie: Make X Y  (przypisz wartość Y do X)
def p_statement_make(p):
    'statement : MAKE ID expression'
    p[0] = f"{p[2]} = {p[3]}"

# Print
def p_statement_print(p):
    'statement : PRINT expression'
    p[0] = f"print({p[2]})"

# If
def p_statement_if(p):
    'statement : IF expression COLON statements EXCLAIM'
    p[0] = f"if {p[2]}:\n{_indent(p[4])}"

def p_statement_if_else(p):
    'statement : IF expression COLON statements EXCLAIM ELSE COLON statements EXCLAIM'
    p[0] = f"if {p[2]}:\n{_indent(p[4])}\nelse:\n{_indent(p[8])}"

def p_statement_if_elif(p):
    'statement : IF expression COLON statements EXCLAIM ELSE_IF expression COLON statements EXCLAIM'
    p[0] = f"if {p[2]}:\n{_indent(p[4])}\nelif {p[7]}:\n{_indent(p[9])}"

def p_statement_if_elif_else(p):
    'statement : IF expression COLON statements EXCLAIM ELSE_IF expression COLON statements EXCLAIM ELSE COLON statements EXCLAIM'
    p[0] = f"if {p[2]}:\n{_indent(p[4])}\nelif {p[7]}:\n{_indent(p[9])}\nelse:\n{_indent(p[13])}"

# While
def p_statement_while(p):
    'statement : AS_LONG_AS expression COLON statements EXCLAIM'
    p[0] = f"while {p[2]}:\n{_indent(p[4])}"

def _indent(code):
    return "\n".join("    " + line for line in code.splitlines())

# ---------- Expressions ----------

def p_expression_binop(p):
    '''expression : expression PLUS  expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OVER  expression'''
    op_map = {'PLUS': '+', 'MINUS': '-', 'TIMES': '*', 'OVER': '/'}
    op = op_map[p.slice[2].type]
    p[0] = f"({p[1]} {op} {p[3]})"

def p_expression_compare(p):
    '''expression : expression LT expression
                  | expression GT expression'''
    op = '<' if p.slice[2].type == 'LT' else '>'
    p[0] = f"({p[1]} {op} {p[3]})"

# Sprawdzenie równości: X is Y?
def p_expression_eq_is(p):
    '''expression : expression IS expression QUESTION
                  | expression ARE expression QUESTION'''
    p[0] = f"({p[1]} == {p[3]})"

def p_expression_logic_and(p):
    'expression : expression AND expression'
    p[0] = f"({p[1]} and {p[3]})"

def p_expression_logic_or(p):
    'expression : expression OR expression'
    p[0] = f"({p[1]} or {p[3]})"

def p_expression_logic_not(p):
    'expression : NOT expression'
    p[0] = f"(not {p[2]})"

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = str(p[1])

def p_expression_id(p):
    'expression : ID'
    p[0] = p[1]

def p_expression_string(p):
    'expression : STRING'
    p[0] = f'"{p[1]}"'

def p_expression_bool(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = "True" if p[1].lower() == 'fact' else "False"

def p_error(p):
    if p:
        print(f"BLAD SKLADNI: Nie rozumiem '{p.value}' (typ: {p.type}) w linii {p.lineno}")
    else:
        print("BLAD SKLADNI: Nieoczekiwany koniec pliku (brakuje 'America is great'?)")

parser = yacc.yacc()

# ==========================================================
# 3. URUCHOMIENIE
# ==========================================================

def run(code):
    # Usuń wieloliniowe stringi (bloki w cudzysłowach z newline)
    # - zamień je na pojedyncze stringi z \n
    code = re.sub(r'"(.*?)"', lambda m: '"' + m.group(1).replace('\n', '\\n') + '"', code, flags=re.DOTALL)
    # Usuń puste linie
    clean = "\n".join(line.strip() for line in code.splitlines() if line.strip())
    print("--- ETAP 1: KONWERSJA ---")
    result = parser.parse(clean, lexer=lexer.clone())
    if result:
        print("Wygenerowany kod Python:\n" + result)
        print("\n--- ETAP 2: URUCHAMIANIE ---")
        try:
            exec(result, {})
        except Exception as e:
            print(f"BLAD WYKONANIA: {e}")
    else:
        print("Nie udalo sie wygenerowac kodu.")

# Wczytaj plik z argumentu lub użyj przykładu
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()
    run(code)
else:
    # Przykład testowy
    trump_code = """
Make Donald 15000000
Nothing is, 1000000 minus 1000000 plus 500000000;
say Nothing
America is great
    """
    run(trump_code)