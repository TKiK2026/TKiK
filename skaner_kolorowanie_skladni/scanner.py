from skaner_kolorowanie_skladni.token import *


KEYWORDS = {
    "int", "float", "double", "char", "void", "bool",
    "if", "else", "for", "while", "do", "switch", "case",
    "break", "continue", "return",
    "class", "struct", "public", "private", "protected",
    "virtual", "override", "const", "auto", "static",
    "using", "namespace","include", "define",
    "true", "false", "nullptr", "new", "delete"
}


class Scanner:
    def __init__(self,text):
        self.text = text
        self.pos = 0
        self.n = len(text)

    def scan_whitespace(self):
        start = self.pos

        while self.pos < self.n and self.text[self.pos].isspace():
            self.pos+=1

        return Token(TokenType.WHITESPACE, self.text[start:self.pos])

    def scan_identifier(self):
        start = self.pos

        while self.pos < self.n and (self.text[self.pos].isdigit() or self.text[self.pos].isalpha() or self.text[self.pos]=='_'):
            self.pos += 1

        value = self.text[start:self.pos]

        if value in KEYWORDS:
            return Token(TokenType.KEYWORD, value)

        return Token(TokenType.IDENTIFIER, value)

    def scan_number(self):
        start = self.pos

        while self.pos < self.n and (self.text[self.pos].isdigit()):
            self.pos += 1

        if self.text[self.pos] == '.':
            self.pos += 1
            while self.pos < self.n and (self.text[self.pos].isdigit()):
                self.pos += 1

        return Token(TokenType.NUMBER, self.text[start:self.pos])

    def scan_string(self):
        quote = self.text[self.pos]
        start = self.pos
        self.pos+=1

        while self.pos < self.n and self.text[self.pos] != quote:
            if self.text[self.pos] == '\\':  # escape
                self.pos+=2
            else:
                self.pos+=1

        if self.text[self.pos] == quote:
            self.pos += 1

        return Token(TokenType.STRING, self.text[start:self.pos])

    def scan_line_comment(self):
        start = self.pos

        while self.pos < self.n and self.text[self.pos] != '\n':
            self.pos+=1
        return Token(TokenType.COMMENT, self.text[start:self.pos])

    def scan_block_comment(self):
        start = self.pos
        self.pos+=2  # /*

        while self.pos<self.n and not (self.text[self.pos] == '*' and (self.pos+1 < self.n and self.text[self.pos+1] == '/')):
            self.pos+=1

        if self.pos<self.n:
            self.pos+=2  # */
            
        return Token(TokenType.COMMENT, self.text[start:self.pos])

    def scan_operator(self):
        if self.pos+1 < self.n:
            two = self.text[self.pos:self.pos+2]
            if two in {
                "==", "!=", "<=", ">=", "++", "--",
                "+=", "-=", "*=", "/=", "&&", "||",
                "->", "::"
            }:
                self.pos+=2
                return Token(TokenType.OPERATOR, two)

        self.pos+=1
        return Token(TokenType.OPERATOR, self.text[self.pos-1])

    def scan_symbol(self):
        self.pos+=1
        return Token(TokenType.SYMBOL, self.text[self.pos-1])

    def scan_token(self):
        if self.pos >= self.n:
            return Token(TokenType.EOF, None)

        current_char = self.text[self.pos]

        if current_char == '/' and (self.pos+1 < self.n and self.text[self.pos+1] == '/'):
            return self.scan_line_comment()

        if current_char == '/' and (self.pos+1 < self.n and self.text[self.pos+1] == '*'):
            return self.scan_block_comment()

        if current_char.isspace():
            return self.scan_whitespace()

        if current_char in {'"', "'"}:
            return self.scan_string()

        if current_char.isalpha() or current_char == '_':
            return self.scan_identifier()

        if current_char.isdigit():
            return self.scan_number()

        if current_char in "+-*/=%!<>:&|^~":
            return self.scan_operator()

        if current_char in "#{}[]();,.":
            return self.scan_symbol()

        self.pos+=1
        return Token(TokenType.ERROR, current_char)
