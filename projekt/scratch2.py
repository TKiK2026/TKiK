import ply.lex as lex
import ply.yacc as yacc


tokens = (
    "ID", "STRING", "PLUS", "MINUS",
    "ASSIGN_OP_IS", "ASSIGN_OP_ARE", "ASSIGN_OP_SIGN",
    "MAKE", "PRINT", "NUMBER", "TIMES", "OVER",
    "AMERICA_GREAT", "FACT", "LIE", "LPAREN", "RPAREN",
    "LBRACE", "RBRACE", "IF", "ELSE", "GREATER", "LESS",
    "QUESTION", "GE", "LE", "GT", "LT", "EQ", "AND", "OR",
    "AS", "LONG"
)
t_LPAREN = r','
t_RPAREN = r';'
t_LBRACE = r':'
t_RBRACE = r'!'
t_ignore = ' \t.'
t_QUESTION = r'\?'
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


def t_AMERICA_GREAT(t):
    r"""America\s+is\s+great\."""
    return t

def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    val = t.value.lower()
    keywords = {
        'is': 'ASSIGN_OP_IS',
        'are': 'ASSIGN_OP_ARE',
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
        'more': 'GREATER', 'greater': 'GREATER', 'larger': 'GREATER',
        'less': 'LESS', 'fewer': 'LESS', 'smaller': 'LESS',
        'and': 'AND', 'or': 'OR',
        'as': 'AS', 'long': 'LONG'
    }
    t.type = keywords.get(val, 'ID')
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1]
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
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'ASSIGN_OP_IS', 'ASSIGN_OP_ARE', 'ASSIGN_OP_SIGN', 'GE', 'LE', 'GT', 'LT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'OVER'),
)


def p_program(p):
    """program : body AMERICA_GREAT"""
    p[0] = p[1]

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
                | loop_statement"""
    p[0] = p[1]

def p_assignment(p):
    """assignment : ID ASSIGN_OP_SIGN expression
                  | ID ASSIGN_OP_IS expression
                  | ID ASSIGN_OP_ARE expression
                  | MAKE ID expression"""
    if len(p) == 4:
        if p[1].lower() == "make":
            p[0] = ("assign", p[2], p[3])
        else:
            p[0] = ("assign", p[1], p[3])

def p_print(p):
    """print_statement : PRINT expression"""
    p[0] = ('print', p[2])

def p_if_statement(p):
    """if_statement : IF comparison LBRACE body RBRACE
                    | IF comparison LBRACE body RBRACE ELSE LBRACE body RBRACE
                    | IF comparison LBRACE body RBRACE ELSE if_statement"""
    if len(p) == 6:
        p[0] = ('if', p[2], p[4])
    elif len(p) == 10:
        p[0] = ('if_else', p[2], p[4], p[8])
    elif len(p) == 8:
        p[0] = ('if_else', p[2], p[4], [p[7]])

def p_loop_statement(p):
    """loop_statement : AS LONG AS comparison LBRACE body RBRACE"""
    p[0] = ('while', p[4], p[6])

def p_comparison(p):
    """comparison : expression EQ expression
                  | expression GREATER expression
                  | expression LESS expression
                  | expression GE expression
                  | expression LE expression
                  | expression GT expression
                  | expression LT expression"""
    if len(p) == 4:
        type_map = {'EQ': 'EQ', 'GE': 'GREATER_EQUAL', 'LE': 'LESS_EQUAL', 'GT': 'GREATER', 'LT': 'LESS'}
        op_type = p.slice[2].type
        p[0] = (type_map.get(op_type, op_type), p[1], p[3])
    else:
        op = 'GREATER_EQUAL' if p[2].lower() == 'greater' else 'LESS_EQUAL'
        p[0] = (op, p[1], p[4])

def p_comparison_group(p):
    """comparison : LPAREN comparison RPAREN"""
    p[0] = p[2]

def p_comparison_or(p):
    """comparison : comparison OR comparison"""
    p[0] = ('OR', p[1], p[3])

def p_comparison_and(p):
    """comparison : comparison AND comparison"""
    p[0] = ('AND', p[1], p[3])

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OVER expression"""
    p[0] = (p.slice[2].type, p[1], p[3])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_expression_value(p):
    """expression : value"""
    p[0] = p[1]

def p_question_expr(p):
    """question_expr : expression ASSIGN_OP_IS expression QUESTION
                     | expression ASSIGN_OP_ARE expression QUESTION
                     | expression ASSIGN_OP_SIGN expression QUESTION
                     | expression GREATER expression QUESTION
                     | expression LESS expression QUESTION
                     | expression GE expression QUESTION
                     | expression LE expression QUESTION
                     | expression GT expression QUESTION
                     | expression LT expression QUESTION"""
    if len(p) == 5:
        type_map = {'ASSIGN_OP_IS': 'ASSIGN_OP', 'ASSIGN_OP_ARE': 'ASSIGN_OP', 'ASSIGN_OP_SIGN': 'ASSIGN_OP',
                    'GE': 'GREATER_EQUAL', 'LE': 'LESS_EQUAL', 'GT': 'GREATER', 'LT': 'LESS'}
        token_type = p.slice[2].type
        p[0] = (type_map.get(token_type, token_type), p[1], p[3])
    else:
        op = 'GREATER_EQUAL' if p[2].lower() == 'greater' else 'LESS_EQUAL'
        p[0] = (op, p[1], p[4])

def p_value(p):
    """value : NUMBER
             | STRING
             | ID
             | LIE
             | FACT
             | question_expr"""
    if len(p) == 2:
        if isinstance(p[1], tuple):
            p[0] = p[1]
        elif p.slice[1].type == 'FACT':
            p[0] = True
        elif p.slice[1].type == 'LIE':
            p[0] = False
        else:
            p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax Error near '{p.value}'")
    else:
        print("Syntax Error at EOF")


lexer = lex.lex()

def type_error(op, l, r):
    print(f"Type error: {l} {op} {r}")
    return 0

def evaluate(exp, variables):
    if not isinstance(exp, tuple):
        if isinstance(exp, int) or isinstance(exp, bool): return exp
        if isinstance(exp, str) and exp in variables: return variables[exp]
        return exp

    op, l, r = exp
    op = op.upper()
    left_val = evaluate(l, variables)
    right_val = evaluate(r, variables)

    if op == 'PLUS':
        if isinstance(left_val, str) or isinstance(right_val, str):
            def to_str(val):
                if val is True: return "fact"
                if val is False: return "lie"
                return str(val)
            return to_str(left_val) + to_str(right_val)

        if isinstance(left_val, bool) or isinstance(right_val, bool):
            print("Error: You can't add facts and lies together!")
            return 0

        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val + right_val

        return type_error('+', left_val, right_val)

    if op == 'MINUS': return left_val - right_val
    if op == 'TIMES': return left_val * right_val
    if op == 'OVER':
        if right_val == 0:
            print("Error: Dividing by zero? Not in this country!")
            return 0
        return left_val / right_val

    if op == 'ASSIGN_OP': return left_val == right_val
    if op == 'EQ': return left_val == right_val
    if op == 'GREATER': return left_val > right_val
    if op == 'LESS': return left_val < right_val
    if op == 'GREATER_EQUAL': return left_val >= right_val
    if op == 'LESS_EQUAL': return left_val <= right_val
    if op == 'AND': return bool(left_val) and bool(right_val)
    if op == 'OR': return left_val or right_val

    return 0

def run_interpreter(instructions, variables=None):
    if variables is None: variables = {}

    for instr in instructions:
        type = instr[0]

        if type == "assign":
            var_name = instr[1]
            variables[var_name] = evaluate(instr[2], variables)
        elif type == "print":
            val = evaluate(instr[1], variables)
            if val is True:
                print("Fact")
            elif val is False:
                print("Lie")
            else:
                print(val)
        elif type == "if":
            if evaluate(instr[1], variables): run_interpreter(instr[2], variables)
        elif type == "if_else":
            if evaluate(instr[1], variables):
                run_interpreter(instr[2], variables)
            else:
                run_interpreter(instr[3], variables)
        elif type == "while":
            while evaluate(instr[1], variables): run_interpreter(instr[2], variables)

    return variables


parser = yacc.yacc()

data = """
wall = 100
wall is 150
make is_huge wall >= 50 ?
say "Is the wall huge using symbols?"
say is_huge

say "--- Testing Math & Types ---"
say "Wall is " + wall + " meters long."
say "Adding fact to a text: " + fact
say "This will fail: "
make fail fact + lie

wall are 100

say "--- Testing If Statements ---"
if wall == 100 :
    say "The wall is exactly 100 (checked with ==)"
!
make wall 150
say wall is 150?

wall = 100

say "--- Testing Loop ---"
as long as wall < 103 :
    say "Building wall..."
    make wall wall + 1
!

say "--- Testing Else If & Logic ---"
if wall == 50 or wall < 100 :
    say "Wall is small"
! else if ,wall > 100; and ,wall < 200; :
    say "Wall is huge and perfect!"
! else :
    say "Wall is something else"
!

say "--- Testing Questions ---"
make is_safe wall is 103 ?
say "Is the wall safe?"
say is_safe

America is great.
"""

result = parser.parse(data, lexer=lexer)

if result:
    print("--- Program Wykonany ---")
    run_interpreter(result)
