from lexer import Lexer, TokenType


# ── AST Node Classes ──────────────────────────────────────────────────────────

class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"


class AssignmentNode:
    def __init__(self, name, value):
        self.name  = name    # string, e.g. "x"
        self.value = value   # an expression node

    def __repr__(self):
        return f"AssignmentNode({self.name}, {self.value})"


class IfNode:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition   = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfNode({self.condition}, then={self.then_branch}, else={self.else_branch})"


class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body      = body

    def __repr__(self):
        return f"WhileNode({self.condition}, body={self.body})"


class PrintNode:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"PrintNode({self.expression})"


class ConditionNode:
    def __init__(self, left, operator, right):
        self.left     = left
        self.operator = operator
        self.right    = right

    def __repr__(self):
        return f"ConditionNode({self.left} {self.operator} {self.right})"


class BinaryOpNode:
    def __init__(self, left, operator, right):
        self.left     = left
        self.operator = operator
        self.right    = right

    def __repr__(self):
        return f"BinaryOpNode({self.left} {self.operator} {self.right})"


class NumberNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"


class IdentifierNode:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdentifierNode({self.name})"


# ── Pretty Printer ────────────────────────────────────────────────────────────

def print_tree(node, indent=0):
    pad = "  " * indent

    if isinstance(node, ProgramNode):
        print(pad + "ProgramNode")
        for stmt in node.statements:
            print_tree(stmt, indent + 1)

    elif isinstance(node, AssignmentNode):
        print(pad + f"AssignmentNode: {node.name} =")
        print_tree(node.value, indent + 1)

    elif isinstance(node, IfNode):
        print(pad + "IfNode")
        print(pad + "  condition:")
        print_tree(node.condition, indent + 2)
        print(pad + "  then:")
        for stmt in node.then_branch:
            print_tree(stmt, indent + 2)
        if node.else_branch:
            print(pad + "  else:")
            for stmt in node.else_branch:
                print_tree(stmt, indent + 2)

    elif isinstance(node, WhileNode):
        print(pad + "WhileNode")
        print(pad + "  condition:")
        print_tree(node.condition, indent + 2)
        print(pad + "  body:")
        for stmt in node.body:
            print_tree(stmt, indent + 2)

    elif isinstance(node, PrintNode):
        print(pad + "PrintNode")
        print_tree(node.expression, indent + 1)

    elif isinstance(node, ConditionNode):
        print(pad + f"ConditionNode: {node.operator}")
        print_tree(node.left,  indent + 1)
        print_tree(node.right, indent + 1)

    elif isinstance(node, BinaryOpNode):
        print(pad + f"BinaryOpNode: {node.operator}")
        print_tree(node.left,  indent + 1)
        print_tree(node.right, indent + 1)

    elif isinstance(node, NumberNode):
        print(pad + f"NumberNode: {node.value}")

    elif isinstance(node, IdentifierNode):
        print(pad + f"IdentifierNode: {node.name}")


# ── Parser Class ──────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, source):
        self.lexer   = Lexer(source)
        self.current = self.lexer.get_next_token()

    def consume(self):
        """Move to the next token."""
        self.current = self.lexer.get_next_token()

    def expect(self, token_type):
        """Consume a token of the expected type, or raise an error."""
        if self.current.type != token_type:
            raise Exception(
                f"SyntaxError: Expected {token_type} but got "
                f"{self.current.type} ('{self.current.value}')"
            )
        self.consume()

    def skip_newlines(self):
        """Skip any newline tokens."""
        while self.current.type == TokenType.TOK_NEWLINE:
            self.consume()

    # ── Grammar Rules ─────────────────────────────────────────────────────────

    def parse_program(self):
        statements = []
        self.skip_newlines()
        while self.current.type != TokenType.TOK_EOF:
            statements.append(self.parse_statement())
            self.skip_newlines()
        return ProgramNode(statements)

    def parse_statement(self):
        if self.current.type == TokenType.TOK_IDENT:
            return self.parse_assignment()
        elif self.current.type == TokenType.TOK_IF:
            return self.parse_if()
        elif self.current.type == TokenType.TOK_WHILE:
            return self.parse_while()
        elif self.current.type == TokenType.TOK_PRINT:
            return self.parse_print()
        else:
            raise Exception(
                f"SyntaxError: Unexpected token {self.current.type} "
                f"('{self.current.value}')"
            )

    def parse_assignment(self):
        name = self.current.value   # e.g. "x"
        self.consume()              # consume the identifier
        self.expect(TokenType.TOK_ASSIGN)
        value = self.parse_expression()
        return AssignmentNode(name, value)

    def parse_if(self):
        self.consume()              # consume 'if'
        condition = self.parse_condition()
        self.expect(TokenType.TOK_COLON)
        self.skip_newlines()
        then_branch = self.parse_block()
        else_branch = None

        self.skip_newlines()
        if self.current.type == TokenType.TOK_ELSE:
            self.consume()          # consume 'else'
            self.expect(TokenType.TOK_COLON)
            self.skip_newlines()
            else_branch = self.parse_block()

        return IfNode(condition, then_branch, else_branch)

    def parse_while(self):
        self.consume()              # consume 'while'
        condition = self.parse_condition()
        self.expect(TokenType.TOK_COLON)
        self.skip_newlines()
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_print(self):
        self.consume()              # consume 'print'
        self.expect(TokenType.TOK_LPAREN)
        expression = self.parse_expression()
        self.expect(TokenType.TOK_RPAREN)
        return PrintNode(expression)

    def parse_block(self):
        statements = []
        if self.current.type == TokenType.TOK_INDENT:
            self.consume()          # consume INDENT
            self.skip_newlines()
            while self.current.type != TokenType.TOK_DEDENT and \
                  self.current.type != TokenType.TOK_EOF:
                statements.append(self.parse_statement())
                self.skip_newlines()
            self.expect(TokenType.TOK_DEDENT)
        else:
            # Single statement block (no indentation)
            statements.append(self.parse_statement())
        return statements

    def parse_condition(self):
        left     = self.parse_expression()
        operator = self.current.value
        self.consume()              # consume the comparison operator
        right    = self.parse_expression()
        return ConditionNode(left, operator, right)

    def parse_expression(self):
        left = self.parse_term()
        while self.current.type in (TokenType.TOK_PLUS, TokenType.TOK_MINUS):
            operator = self.current.value
            self.consume()
            right = self.parse_term()
            left  = BinaryOpNode(left, operator, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current.type in (TokenType.TOK_STAR, TokenType.TOK_SLASH):
            operator = self.current.value
            self.consume()
            right = self.parse_factor()
            left  = BinaryOpNode(left, operator, right)
        return left

    def parse_factor(self):
        if self.current.type == TokenType.TOK_NUMBER:
            value = self.current.value
            self.consume()
            return NumberNode(value)
        elif self.current.type == TokenType.TOK_IDENT:
            name = self.current.value
            self.consume()
            return IdentifierNode(name)
        elif self.current.type == TokenType.TOK_LPAREN:
            self.consume()
            node = self.parse_expression()
            self.expect(TokenType.TOK_RPAREN)
            return node
        else:
            raise Exception(
                f"SyntaxError: Unexpected token {self.current.type} "
                f"('{self.current.value}')"
            )