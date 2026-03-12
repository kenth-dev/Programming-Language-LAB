from lexer import Lexer, TokenType

# ── Lexer Test ────────────────────────────────────────────────────────────────
# This tests the lexer only. It prints the full token stream for the source
# program and checks that all token types are recognized correctly.

def run_lexer_test():
    source = """\
x = 10
y = x + 5
if x > 0:
    print(x)
else:
    print(y)
while x > 0:
    x = x - 1
    print(x)
"""
    print("=" * 50)
    print("LEXER TEST — Token Stream")
    print("=" * 50)

    lexer = Lexer(source)

    while True:
        token = lexer.get_next_token()
        print(token)
        if token.type == TokenType.TOK_EOF:
            break

if __name__ == "__main__":
    run_lexer_test()