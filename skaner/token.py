from enum import Enum, auto


class TokenType(Enum):
    INT    = auto()
    ID     = auto()
    PLUS   = auto()
    MINUS  = auto()
    MUL    = auto()
    DIV    = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF    = auto()
    ERROR  = auto()

    def __str__(self):
        return self.name

class Token:
    def __init__(self, code, value, column):
        self.code = code
        self.value = value
        self.column = column

    def __repr__(self):
        return f"{self.value} {self.code}: {self.column}"
