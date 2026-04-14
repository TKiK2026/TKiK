def p_program(p):
    """program : body AMERICA_GREAT"""

def p_body(p):
    """body : statement
            | body statement"""

def p_statement(p):
    """statement : assignment
                | print_statement
                | if_statement
                | loop_statement"""

def p_assignment(p):
    """assignment : ID ASSIGN_OP_SIGN expression
                  | ID ASSIGN_OP_IS expression
                  | ID ASSIGN_OP_ARE expression
                  | MAKE ID expression"""

def p_print(p):
    """print_statement : PRINT expression"""

def p_if_statement(p):
    """if_statement : IF comparison LBRACE body RBRACE
                    | IF comparison LBRACE body RBRACE ELSE LBRACE body RBRACE
                    | IF comparison LBRACE body RBRACE ELSE if_statement"""

def p_loop_statement(p):
    """loop_statement : AS_LONG_AS comparison LBRACE body RBRACE"""

def p_comparison(p):
    """comparison : expression EQ expression
                  | expression GREATER expression
                  | expression LESS expression
                  | expression GE expression
                  | expression LE expression
                  | expression GT expression
                  | expression LT expression"""

def p_comparison_group(p):
    """comparison : LPAREN comparison RPAREN"""

def p_comparison_or(p):
    """comparison : comparison OR comparison"""

def p_comparison_and(p):
    """comparison : comparison AND comparison"""

def p_expression_or(p):
    """expression : expression OR expression"""

def p_expression_and(p):
    """expression : expression AND expression"""

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OVER expression"""

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""

def p_expression_value(p):
    """expression : value"""

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

def p_value(p):
    """value : NUMBER
             | STRING
             | ID
             | LIE
             | FACT
             | question_expr"""
