from lexer import Lexer, TokenType
from parser import Parser, print_tree
from semantic import SemanticChecker


# ── End-to-End Pipeline Test ──────────────────────────────────────────────────
# This tests one source program through all 3 stages:
# 1) Lexer token stream
# 2) Parser AST
# 3) Semantic analysis

def run_pipeline_test():
    source = """\
x = 5 + 3
y = x * 2
if y > 10:
    print(y)
else:
    print(x)
"""

    print("=" * 50)
    print("PIPELINE TEST — One Source Through Lexer, Parser, Semantic")
    print("=" * 50)
    print("SOURCE:\n")
    print(source)

    print("\n" + "=" * 50)
    print("1) LEXER OUTPUT")
    print("=" * 50)
    lexer = Lexer(source)
    while True:
        token = lexer.get_next_token()
        print(token)
        if token.type == TokenType.TOK_EOF:
            break

    print("\n" + "=" * 50)
    print("2) PARSER OUTPUT")
    print("=" * 50)
    parser = Parser(source)
    tree = parser.parse_program()
    print_tree(tree)

    print("\n" + "=" * 50)
    print("3) SEMANTIC OUTPUT")
    print("=" * 50)
    semantic_parser = Parser(source)
    semantic_tree = semantic_parser.parse_program()
    checker = SemanticChecker()
    checker.check(semantic_tree)


if __name__ == "__main__":
    run_pipeline_test()
