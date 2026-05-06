import pprint
from lexer import lexer
from parser import parser
from transpiler import translate_to_python

test_cases = [
    """
    make wall "high"
    as long as wall is "high":
        wall is "small"
        if wall is "small":
            stop!
    !
    America is great.
    """,
]

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    for i, code in enumerate(test_cases, 1):
        print("=" * 60)
        print(f"TEST #{i}")
        print("=" * 60)
        print("KOD ŹRÓDŁOWY (TrumpScript):")
        print(code.strip())

        ast = parser.parse(code)

        print("\nDRZEWO SKŁADNIOWE (AST):")
        pp.pprint(ast)

        python_code = translate_to_python(ast)

        print("\nWYGENEROWANY KOD (Python):")
        print(python_code)
        print()