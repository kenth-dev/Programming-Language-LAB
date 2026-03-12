import re
from enum import Enum


# ── Token Types ───────────────────────────────────────────────────────────────

class TokenType(Enum):
    # Keywords
    TOK_IF      = "IF"
    TOK_ELSE    = "ELSE"
    TOK_WHILE   = "WHILE"
    TOK_PRINT   = "PRINT"

    # Operators
    TOK_ASSIGN  = "ASSIGN"
    TOK_PLUS    = "PLUS"
    TOK_MINUS   = "MINUS"
    TOK_STAR    = "STAR"
    TOK_SLASH   = "SLASH"
    TOK_GT      = "GT"
    TOK_LT      = "LT"
    TOK_GTE     = "GTE"
    TOK_LTE     = "LTE"
    TOK_EQ      = "EQ"
    TOK_NEQ     = "NEQ"

    # Delimiters
    TOK_LPAREN  = "LPAREN"
    TOK_RPAREN  = "RPAREN"
    TOK_LBRACE  = "LBRACE"
    TOK_RBRACE  = "RBRACE"
    TOK_SEMI    = "SEMI"
    TOK_COLON   = "COLON"

    # Identifiers and Literals
    TOK_IDENT   = "IDENT"
    TOK_NUMBER  = "NUMBER"
    TOK_STRING  = "STRING"

    # Whitespace / Structure
    TOK_NEWLINE = "NEWLINE"
    TOK_INDENT  = "INDENT"
    TOK_DEDENT  = "DEDENT"

    # Special
    TOK_EOF     = "EOF"
    TOK_UNKNOWN = "UNKNOWN"


# ── Token Class ───────────────────────────────────────────────────────────────

class Token:
    def __init__(self, type, value):
        self.type  = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


# ── Keywords ──────────────────────────────────────────────────────────────────

KEYWORDS = {
    "if":    TokenType.TOK_IF,
    "else":  TokenType.TOK_ELSE,
    "while": TokenType.TOK_WHILE,
    "print": TokenType.TOK_PRINT,
}


# ── Token Patterns ────────────────────────────────────────────────────────────
# Order matters: longer/more specific patterns must come before shorter ones.

TOKEN_PATTERNS = [
    (TokenType.TOK_STRING,  r'"[a-zA-Z ]*"'),
    (TokenType.TOK_NUMBER,  r'[0-9]+(\.[0-9]+)?'),
    (TokenType.TOK_IDENT,   r'[a-zA-Z_][a-zA-Z0-9_]*'),
    (TokenType.TOK_GTE,     r'>='),
    (TokenType.TOK_LTE,     r'<='),
    (TokenType.TOK_EQ,      r'=='),
    (TokenType.TOK_NEQ,     r'!='),
    (TokenType.TOK_ASSIGN,  r'='),
    (TokenType.TOK_PLUS,    r'\+'),
    (TokenType.TOK_MINUS,   r'-'),
    (TokenType.TOK_STAR,    r'\*'),
    (TokenType.TOK_SLASH,   r'/'),
    (TokenType.TOK_GT,      r'>'),
    (TokenType.TOK_LT,      r'<'),
    (TokenType.TOK_LPAREN,  r'\('),
    (TokenType.TOK_RPAREN,  r'\)'),
    (TokenType.TOK_LBRACE,  r'\{'),
    (TokenType.TOK_RBRACE,  r'\}'),
    (TokenType.TOK_SEMI,    r';'),
    (TokenType.TOK_COLON,   r':'),
]


# ── Lexer Class ───────────────────────────────────────────────────────────────

class Lexer:
    def __init__(self, source):
        self.source       = source
        self.pos          = 0
        self.line         = 1
        self.indent_stack = [0]   # tracks indentation levels
        self.token_queue  = []    # holds queued INDENT/DEDENT/NEWLINE tokens

    def get_next_token(self):
        # Return any queued tokens first (from INDENT/DEDENT handling)
        if self.token_queue:
            return self.token_queue.pop(0)

        # Skip horizontal whitespace (spaces, tabs) but NOT newlines
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            self.pos += 1

        # Skip comments (# to end of line)
        if self.pos < len(self.source) and self.source[self.pos] == '#':
            while self.pos < len(self.source) and self.source[self.pos] != '\n':
                self.pos += 1

        # End of input — emit remaining DEDENTs before EOF
        if self.pos >= len(self.source):
            if len(self.indent_stack) > 1:
                self.indent_stack.pop()
                return Token(TokenType.TOK_DEDENT, "DEDENT")
            return Token(TokenType.TOK_EOF, None)

        # Handle newlines and track indentation changes
        if self.source[self.pos] == '\n':
            self.pos  += 1
            self.line += 1

            # Count leading spaces on the next line
            indent = 0
            while self.pos < len(self.source) and self.source[self.pos] in ' \t':
                indent += 1
                self.pos += 1

            current_indent = self.indent_stack[-1]

            if indent > current_indent:
                # Indentation increased — emit INDENT
                self.indent_stack.append(indent)
                self.token_queue.append(Token(TokenType.TOK_INDENT, "INDENT"))
            elif indent < current_indent:
                # Indentation decreased — emit one DEDENT per level closed
                while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent:
                    self.indent_stack.pop()
                    self.token_queue.append(Token(TokenType.TOK_DEDENT, "DEDENT"))

            # Always emit NEWLINE first, then any INDENT/DEDENT tokens
            self.token_queue.insert(0, Token(TokenType.TOK_NEWLINE, "\n"))
            return self.token_queue.pop(0)

        # Try matching each token pattern at the current position
        for token_type, pattern in TOKEN_PATTERNS:
            match = re.match(pattern, self.source[self.pos:])
            if match:
                value     = match.group(0)
                self.pos += len(value)

                # Check if identifier is actually a keyword
                if token_type == TokenType.TOK_IDENT and value in KEYWORDS:
                    return Token(KEYWORDS[value], value)

                return Token(token_type, value)

        # No pattern matched — unknown character
        bad_char  = self.source[self.pos]
        self.pos += 1
        raise Exception(f"LexError [line {self.line}]: Unexpected character '{bad_char}'")