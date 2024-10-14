import re
from typing import List, NamedTuple, Optional

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

# Define token types and their regular expressions
token_specification = [
    ('WHITESPACE',    r'[ \t\n\r]+'),                              # Whitespace
    ('STRING',        r'"(?:\\["\\/bfnrt]|\\u[0-9a-fA-F]{4}|[^"\\])*"'),  # String
    ('NUMBER',        r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?'),    # Number
    ('TRUE',          r'true'),                                    # true
    ('FALSE',         r'false'),                                   # false
    ('NULL',          r'null'),                                    # null
    ('LEFT_BRACE',    r'\{'),                                      # {
    ('RIGHT_BRACE',   r'\}'),                                      # }
    ('LEFT_BRACKET',  r'\['),                                      # [
    ('RIGHT_BRACKET', r'\]'),                                      # ]
    ('COMMA',         r','),                                       # ,
    ('COLON',         r':'),                                       # :
]

# Compile the regular expressions
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
get_token = re.compile(token_regex).match

class Lexer:
    def __init__(self, input_string: str):
        self.input = input_string
        self.len_input = len(input_string)
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.position < self.len_input:
            match = get_token(self.input, self.position)
            if not match:
                invalid_char = self.input[self.position]
                raise ValueError(f"Unexpected character '{invalid_char}' at line {self.line}, column {self.column}")

            kind = match.lastgroup
            value = match.group(kind)
            if kind == 'WHITESPACE':
                # Update line and column numbers
                line_breaks = value.count('\n')
                if line_breaks > 0:
                    self.line += line_breaks
                    self.column = len(value) - value.rfind('\n')
                else:
                    self.column += len(value)
            else:
                tokens.append(Token(kind, value, self.line, self.column))
                self.column += len(value)
            self.position = match.end()
        tokens.append(Token('EOF', '', self.line, self.column))
        return tokens

def lex(input_string: str) -> List[Token]:
    lexer = Lexer(input_string)
    return lexer.tokenize()
