def p_program(p):
    """program : body AMERICA_GREAT
               | AMERICA_GREAT"""

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
                  | ID ASSIGN_OP_WORD expression
                  | MAKE ID expression"""

def p_print(p):
    """print_statement : PRINT expression"""

def p_if_statement(p):
    """if_statement : IF expression LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE LBRACE body RBRACE
                    | IF expression LBRACE body RBRACE ELSE if_statement"""

def p_loop_statement(p):
    """loop_statement : AS_LONG_AS expression LBRACE body RBRACE"""

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OVER expression
                  | expression AND expression
                  | expression OR expression"""

def p_expression_comparison(p):
    """expression : expression EQ expression
                  | expression GE expression
                  | expression LE expression
                  | expression GT expression
                  | expression LT expression
                  | expression ASSIGN_OP_WORD expression"""

def p_expression_question(p):
    """expression : expression QUESTION"""

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""

def p_expression_value(p):
    """expression : NUMBER
                  | STRING
                  | ID
                  | FACT
                  | LIE"""
