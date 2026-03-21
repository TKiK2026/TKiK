from skaner_wyrazenie_matematyczne.scanner import Scanner
from skaner_wyrazenie_matematyczne.token import *


def main():
    text = input("Podaj wyrażenie: ")
    scanner = Scanner(text)

    while True:
        token = scanner.scan_token()
        print(token)

        if token.code == TokenType.EOF:
            break

if __name__ == "__main__":
    main()
