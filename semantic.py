from parser import (
    ProgramNode,
    AssignmentNode,
    IfNode,
    WhileNode,
    PrintNode,
    ConditionNode,
    BinaryOpNode,
    NumberNode,
    IdentifierNode,
)


# ── Symbol Table ─────────────────────────────────────────────────────────────

class SymbolTable:
    def __init__(self):
        self.table = {}  # { name: { "line": int, "initialized": bool } }

    def declare(self, name, line):
        """Add a variable to the table. Error if already declared."""
        if name in self.table:
            raise Exception(
                f"SemanticError [line {line}]: "
                f"Variable '{name}' is already declared."
            )
        self.table[name] = {"line": line, "initialized": False}

    def lookup(self, name):
        """Return the variable entry or None if not found."""
        return self.table.get(name, None)

    def set_initialized(self, name):
        """Mark a variable as assigned/initialized."""
        if name in self.table:
            self.table[name]["initialized"] = True

    def is_initialized(self, name):
        """Check if a variable has been assigned a value."""
        entry = self.table.get(name, None)
        if entry is None:
            return False
        return entry["initialized"]


# ── Semantic Checker ─────────────────────────────────────────────────────────

class SemanticChecker:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def error(self, msg):
        """Record a semantic error."""
        self.errors.append(msg)
        print(msg)

    def check(self, node):
        """Entry point — start walking the AST from the root."""
        self.predeclare_assignments(node)
        self.visit(node)
        if not self.errors:
            print("Semantic analysis passed. No errors found.")

    def predeclare_assignments(self, node):
        """Declare all assignment targets before semantic checks."""
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.predeclare_assignments(stmt)
        elif isinstance(node, AssignmentNode):
            if self.symbol_table.lookup(node.name) is None:
                self.symbol_table.declare(node.name, line=0)
            self.predeclare_assignments(node.value)
        elif isinstance(node, IfNode):
            self.predeclare_assignments(node.condition)
            for stmt in node.then_branch:
                self.predeclare_assignments(stmt)
            if node.else_branch:
                for stmt in node.else_branch:
                    self.predeclare_assignments(stmt)
        elif isinstance(node, WhileNode):
            self.predeclare_assignments(node.condition)
            for stmt in node.body:
                self.predeclare_assignments(stmt)
        elif isinstance(node, PrintNode):
            self.predeclare_assignments(node.expression)
        elif isinstance(node, ConditionNode):
            self.predeclare_assignments(node.left)
            self.predeclare_assignments(node.right)
        elif isinstance(node, BinaryOpNode):
            self.predeclare_assignments(node.left)
            self.predeclare_assignments(node.right)

    def visit(self, node):
        """Dispatch to the correct visitor based on node type."""
        if isinstance(node, ProgramNode):
            self.visit_program(node)
        elif isinstance(node, AssignmentNode):
            self.visit_assignment(node)
        elif isinstance(node, IfNode):
            self.visit_if(node)
        elif isinstance(node, WhileNode):
            self.visit_while(node)
        elif isinstance(node, PrintNode):
            self.visit_print(node)
        elif isinstance(node, ConditionNode):
            self.visit_condition(node)
        elif isinstance(node, BinaryOpNode):
            self.visit_binaryop(node)
        elif isinstance(node, IdentifierNode):
            self.visit_identifier(node)
        elif isinstance(node, NumberNode):
            pass
        else:
            self.error(f"SemanticError: Unknown node type {type(node)}")

    def visit_program(self, node):
        """Visit every statement in the program."""
        for stmt in node.statements:
            self.visit(stmt)

    def visit_assignment(self, node):
        """
        Rule 1 & 2: Declare the variable if first time seen,
        then check the value expression.
        """
        self.visit(node.value)
        self.symbol_table.set_initialized(node.name)

    def visit_identifier(self, node):
        """
        Rule 1 & 3: Check variable is declared and initialized before use.
        """
        entry = self.symbol_table.lookup(node.name)
        if entry is None:
            self.error(
                f"SemanticError: Variable '{node.name}' is used "
                f"but has never been declared."
            )
        elif not self.symbol_table.is_initialized(node.name):
            self.error(
                f"SemanticError: Variable '{node.name}' is used "
                f"before being assigned a value."
            )

    def visit_if(self, node):
        """
        Rule 5: Check condition is valid, then visit both branches.
        """
        self.visit(node.condition)
        for stmt in node.then_branch:
            self.visit(stmt)
        if node.else_branch:
            for stmt in node.else_branch:
                self.visit(stmt)

    def visit_while(self, node):
        """
        Rule 5: Check condition is valid, then visit the body.
        """
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)

    def visit_print(self, node):
        """Check the expression inside print is valid."""
        self.visit(node.expression)

    def visit_condition(self, node):
        """
        Rule 4: Both sides of a condition must be valid numeric expressions.
        """
        valid_ops = [">", "<", ">=", "<=", "==", "!="]
        if node.operator not in valid_ops:
            self.error(
                f"SemanticError: '{node.operator}' is not a valid "
                f"comparison operator."
            )
        self.visit(node.left)
        self.visit(node.right)

    def visit_binaryop(self, node):
        """Both sides of an arithmetic expression must be valid."""
        self.visit(node.left)
        self.visit(node.right)
