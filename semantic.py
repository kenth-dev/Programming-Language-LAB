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


# ── Symbol Table ─────────────────────────────────────────────────

class SymbolTable:
    def __init__(self):
        # A stack of dictionaries. Each dict is one scope.
        # We start with one global scope.
        self.scope_stack = [{}]

    def enter_scope(self):
        """Push a new empty scope onto the stack."""
        self.scope_stack.append({})
        print(f"  [Scope] Entered new scope. Depth: {len(self.scope_stack)}")

    def exit_scope(self):
        """Pop the current scope off the stack."""
        if len(self.scope_stack) > 1:
            exited = self.scope_stack.pop()
            print(f"  [Scope] Exited scope. Variables in scope: {list(exited.keys())}. Depth: {len(self.scope_stack)}")
        else:
            raise Exception("SemanticError: Cannot exit global scope.")

    def declare(self, name, line):
        """Declare a variable in the current (innermost) scope."""
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            raise Exception(
                f"SemanticError [line {line}]: "
                f"Variable '{name}' is already declared in this scope."
            )
        current_scope[name] = { "line": line, "initialized": False }
        print(f"  [Symbol] Declared '{name}' in scope depth {len(self.scope_stack)}")

    def lookup(self, name):
        """Search for a variable from innermost to outermost scope."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None

    def is_declared(self, name):
        """Check if a variable exists in any scope."""
        return self.lookup(name) is not None

    def set_initialized(self, name):
        """Mark a variable as initialized in whichever scope it lives in."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                scope[name]["initialized"] = True
                return

    def is_initialized(self, name):
        """Check if a variable has been assigned a value."""
        entry = self.lookup(name)
        if entry is None:
            return False
        return entry["initialized"]

# ── Semantic Checker ─────────────────────────────────────────────

from parser import (ProgramNode, AssignmentNode, IfNode, WhileNode,
                    PrintNode, ConditionNode, BinaryOpNode,
                    NumberNode, IdentifierNode)

class SemanticChecker:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors       = []

    def error(self, msg):
        """Record and print a semantic error."""
        self.errors.append(msg)
        print(f"  ❌ {msg}")

    def check(self, node):
        """Entry point — start walking the AST from the root."""
        self.visit(node)
        print()
        if not self.errors:
            print("  ✅ Semantic analysis passed. No errors found.")
        else:
            print(f"  ⚠️  Semantic analysis finished with {len(self.errors)} error(s).")

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
            pass  # Numbers are always valid
        else:
            self.error(f"SemanticError: Unknown node type {type(node)}")

    def visit_program(self, node):
        """Visit every statement in the program."""
        for stmt in node.statements:
            self.visit(stmt)

    def visit_assignment(self, node):
        """
        Rule 1 & 2: Check the right-hand side first,
        then declare and initialize the variable.
        """
        # Check the right-hand side expression first
        self.visit(node.value)

        # Declare in current scope if not yet declared
        if not self.symbol_table.is_declared(node.name):
            self.symbol_table.declare(node.name, line=0)

        # Mark as initialized
        self.symbol_table.set_initialized(node.name)

    def visit_identifier(self, node):
        """
        Rule 1 & 3: Variable must be declared and initialized before use.
        """
        if not self.symbol_table.is_declared(node.name):
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
        Rule 5: Check condition, then visit branches in their own scopes.
        """
        self.visit(node.condition)

        # Then branch gets its own scope
        self.symbol_table.enter_scope()
        for stmt in node.then_branch:
            self.visit(stmt)
        self.symbol_table.exit_scope()

        # Else branch gets its own scope
        if node.else_branch:
            self.symbol_table.enter_scope()
            for stmt in node.else_branch:
                self.visit(stmt)
            self.symbol_table.exit_scope()

    def visit_while(self, node):
        """
        Rule 5: Check condition, then visit body in its own scope.
        """
        self.visit(node.condition)

        # While body gets its own scope
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_print(self, node):
        """Check the expression inside print is valid."""
        self.visit(node.expression)

    def visit_condition(self, node):
        """
        Rule 4: Both sides of condition must be valid numeric expressions.
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