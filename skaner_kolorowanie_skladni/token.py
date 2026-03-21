from enum import Enum, auto


class TokenType(Enum):
    KEYWORD    = auto()
    IDENTIFIER = auto()
    NUMBER     = auto()
    STRING     = auto()
    COMMENT    = auto()
    OPERATOR   = auto()
    SYMBOL     = auto()
    WHITESPACE = auto()
    EOF        = auto()
    ERROR      = auto()

    def __str__(self):
        return self.name

class Token:
    def __init__(self, code, value):
        self.code = code
        self.value = value

    def __repr__(self):
        return f'{self.code}:{self.value}'
