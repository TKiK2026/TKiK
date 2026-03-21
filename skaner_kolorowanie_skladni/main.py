from skaner_kolorowanie_skladni.scanner import Scanner
from skaner_kolorowanie_skladni.token import *
from skaner_kolorowanie_skladni.html_converter import *


def main():
    input_file = "input.cpp"
    output_file = "output.html"

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    scanner = Scanner(text)
    tokens = []

    while True:
        t = scanner.scan_token()
        if t.code == TokenType.EOF:
            break
        tokens.append(t)
    write_html(tokens, output_file)

if __name__ == "__main__":
    main()
