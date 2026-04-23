from parser import Parser
from semantic import SemanticChecker


# ── Semantic Test ─────────────────────────────────────────────────────────────
# This tests the semantic analyzer. It parses each sample program,
# runs semantic checks, and prints semantic errors (if any).

def run_semantic_test():
    programs = {
        "Program 1 (Correct)": """\
x = 5 + 3
y = x * 2
print(y)
""",
        "Program 2 (Undeclared variable)": """\
total = price + 10
print(total)
""",
        "Program 3 (Uninitialized variable)": """\
a = 10
b = a + c
c = 5
""",
        "Program 4 (If with undeclared variable)": """\
if x > 0:
    y = 1
else:
    y = 2
print(y)
""",
    }

    print("=" * 50)
    print("SEMANTIC TEST — Semantic Analysis")
    print("=" * 50)

    for name, source in programs.items():
        print(f"\n{'=' * 50}")
        print(f"Testing: {name}")
        print("=" * 50)
        try:
            parser = Parser(source)
            tree = parser.parse_program()
            checker = SemanticChecker()
            checker.check(tree)
        except Exception as error:
            print(error)


if __name__ == "__main__":
    run_semantic_test()
