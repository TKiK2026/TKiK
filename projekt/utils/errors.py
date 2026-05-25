class SemanticError(Exception):
    """Wyjątek zgłaszany w przypadku błędów semantycznych w TrumpScripcie."""
    pass

class LexerError(Exception):
    """Wyjątek zgłaszany przy napotkaniu nieznanego znaku."""
    pass

class ParserError(Exception):
    """Wyjątek zgłaszany przy błędach składniowych."""
    pass