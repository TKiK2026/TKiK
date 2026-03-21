from skaner_kolorowanie_skladni.scanner import Scanner
from skaner_kolorowanie_skladni.token import *


COLOR_MAP = {
    TokenType.KEYWORD:    "#569CD6",
    TokenType.IDENTIFIER: "#9CDCFE",
    TokenType.NUMBER:     "#B5CEA8",
    TokenType.STRING:     "#CE9178",
    TokenType.COMMENT:    "#6A9955",
    TokenType.OPERATOR:   "#D4D4D4",
    TokenType.SYMBOL:     "#D4D4D4",
}


def escape_html(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def write_html(tokens, out_file):
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write('<meta charset="UTF-8">\n')
        f.write("</head>\n")
        f.write('<body style="background:#1e1e1e;">\n')
        f.write('<pre><code style="font-family:Consolas,monospace;">')

        for t in tokens:
            if t.code == TokenType.WHITESPACE:
                f.write(t.value)
            else:
                color = COLOR_MAP.get(t.code, "#FFFFFF")
                val = escape_html(t.value)
                f.write(f'<span style="color:{color};">{val}</span>')

        f.write("</code></pre>\n</body>\n</html>")
