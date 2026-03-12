# MiniPy Programmming Language

A compiler for MiniPy, a simplified Python-like programming language. Built as a series of lab activities, the project covers language design (BNF grammar), lexical analysis (tokenizer/lexer), and syntax analysis (recursive descent parser with AST construction). Written in Python.
---

## Project Structure
```
minipy/
├── lexer.py      # Lexical analyzer — converts source code into tokens
├── parser.py     # Syntax analyzer — builds an AST from tokens
└── main.py       # Entry point — runs the lexer and parser on a source program
```

---

## Features

- **BNF Grammar** — Formally defined grammar for a Python subset
- **Lexer** — Tokenizes source code into a stream of labeled tokens
- **Parser** — Recursive descent parser that constructs an Abstract Syntax Tree
- **AST Pretty Printer** — Prints the AST in a readable, indented tree format

---

## Supported Language Constructs

- Variable assignment — `x = 10`
- Arithmetic expressions — `x + 5`, `x - 1`, `x * 2`, `x / 2`
- Comparison expressions — `x > 0`, `x == 5`, `x != 3`
- If / else statements
- While loops
- Print statements — `print(x)`
- String literals — `print("hello world")`
- Comments — `# this is a comment`

---

