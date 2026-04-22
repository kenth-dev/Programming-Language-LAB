from test_lexer import run_lexer_test
from test_parser import run_parser_test
from test_semantic import run_semantic_test


if __name__ == "__main__":
    run_lexer_test()
    print()
    run_parser_test()
    print()
    run_semantic_test()

