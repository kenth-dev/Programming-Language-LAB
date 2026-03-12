from parser import Parser, print_tree

# ── Parser Test ───────────────────────────────────────────────────────────────
# This tests the parser only. It builds the AST from the source program
# and prints it as a formatted tree. Tests all node types:
#   AssignmentNode, BinaryOpNode, IfNode, WhileNode,
#   PrintNode, ConditionNode, IdentifierNode, NumberNode

def run_parser_test():
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
    print("PARSER TEST — Abstract Syntax Tree")
    print("=" * 50)

    parser = Parser(source)
    tree   = parser.parse_program()
    print_tree(tree)

if __name__ == "__main__":
    run_parser_test()