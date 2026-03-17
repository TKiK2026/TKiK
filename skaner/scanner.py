from token import *


class Scanner:
    def __init__(self,text):
        self.text = "".join(text.split())
        self.pos = 0

    def scan_id(self):
        beg = self.pos

        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos].isalpha() or self.text[self.pos]=='_'):
            self.pos += 1

        return Token(TokenType.ID, self.text[beg:self.pos], beg)

    def scan_integer(self):
        beg = self.pos

        while self.pos < len(self.text) and (self.text[self.pos].isdigit()):
            self.pos += 1

        return Token(TokenType.INT, self.text[beg:self.pos], beg)

    def scan_token(self):
        if self.pos>=len(self.text):
            return Token(TokenType.EOF, None, self.pos)

        current_char = self.text[self.pos]

        if current_char.isdigit():
            return self.scan_integer()

        elif current_char.isalpha() or current_char == '_':
            return self.scan_id()

        elif current_char == '(':
            self.pos+=1
            return Token(TokenType.LPAREN, '(', self.pos-1)

        elif current_char == ')':
            self.pos+=1
            return Token(TokenType.RPAREN, ')', self.pos-1)

        elif current_char == "+":
            self.pos+=1
            return Token(TokenType.PLUS, '+', self.pos-1)

        elif current_char == "-":
            self.pos+=1
            return Token(TokenType.MINUS, '-', self.pos-1)

        elif current_char == "*":
            self.pos+=1
            return Token(TokenType.MUL, '*', self.pos-1)

        elif current_char == "/":
            self.pos+=1
            return Token(TokenType.DIV, '/', self.pos-1)

        self.pos+=1
        return Token(TokenType.ERROR, self.text[self.pos-1], self.pos-1)
