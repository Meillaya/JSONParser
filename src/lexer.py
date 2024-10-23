import re
from typing import List

class Token:
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, line={self.line}, column={self.column})"
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and
                self.value == other.value and
                self.line == other.line and
                self.column == other.column)
    
    def __hash__(self):
        return hash((self.type, self.value, self.line, self.column))

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"LexerError at line {line}, column {column}: {message}")
        self.line = line
        self.column = column

def lex(input_string: str) -> List[Token]:
    tokens = []
    i = 0
    line = 1
    column = 1
    length = len(input_string)

    def advance():
        nonlocal i, line, column
        if i < length:
            if input_string[i] == '\n':
                line += 1
                column = 1
            else:
                column += 1
            i += 1

    def peek():
        return input_string[i] if i < length else ''

    while i < length:
        char = peek()

        # Skip whitespace
        if char in ' \t\r':
            advance()
            continue
        if char == '\n':
            line += 1
            column = 1
            advance()
            continue

        # Single-character tokens
        if char in '{}[],:':
            token_type = {
                '{': 'LEFT_BRACE',
                '}': 'RIGHT_BRACE',
                '[': 'LEFT_BRACKET',
                ']': 'RIGHT_BRACKET',
                ',': 'COMMA',
                ':': 'COLON'
            }[char]
            tokens.append(Token(token_type, char, line, column))
            advance()
            continue

        # Strings
        if char == '"':
            start_line, start_column = line, column
            advance()
            string_value = ''
            while i < length:
                c = peek()
                if c == '"':
                    advance()
                    break
                if c == '\\':
                    advance()
                    if i >= length:
                        raise LexerError("Unterminated string literal", line, column)
                    escape_char = peek()
                    escape_sequences = {
                        '"': '"', '\\': '\\', '/': '/', 'b': '\b',
                        'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'
                    }
                    if escape_char in escape_sequences:
                        string_value += escape_sequences[escape_char]
                        advance()
                    elif escape_char == 'u':
                        unicode_value = 0
                        advance()  # Move past 'u'
                        hex_str = ''
                        for _ in range(4):
                            if i >= length:
                                raise LexerError("Unterminated Unicode escape", line, column)
                            hex_digit = peek()
                            if not re.match(r'[0-9a-fA-F]', hex_digit):
                                raise LexerError(f"Invalid Unicode escape character: {hex_digit}", line, column)
                            hex_str += hex_digit
                            advance()
                        string_value += chr(int(hex_str, 16))
                    else:
                        raise LexerError(f"Invalid escape character: \\{escape_char}", line, column)
                elif ord(c) < 0x20:
                    raise LexerError("Invalid control character in string", line, column)
                else:
                    string_value += c
                    advance()
            else:
                raise LexerError("Unterminated string literal", start_line, start_column)
            tokens.append(Token('STRING', string_value, start_line, start_column))
            continue

        # Numbers
        if char == '-' or char.isdigit():
            start_line, start_column = line, column
            num_str = ''
            if char == '-':
                num_str += '-'
                advance()
                if i >= length or not peek().isdigit():
                    raise LexerError("Invalid number format", line, column)
            if peek() == '0':
                num_str += '0'
                advance()
                if i < length and peek().isdigit():
                    raise LexerError("Numbers cannot have leading zeros", line, column)
            else:
                while i < length and peek().isdigit():
                    num_str += peek()
                    advance()
            if i < length and peek() == '.':
                num_str += '.'
                advance()
                if i >= length or not peek().isdigit():
                    raise LexerError("Invalid number format after decimal point", line, column)
                while i < length and peek().isdigit():
                    num_str += peek()
                    advance()
            if i < length and peek() in ('e', 'E'):
                num_str += peek()
                advance()
                if i < length and peek() in ('+', '-'):
                    num_str += peek()
                    advance()
                if i >= length or not peek().isdigit():
                    raise LexerError("Invalid exponent format", line, column)
                while i < length and peek().isdigit():
                    num_str += peek()
                    advance()
            tokens.append(Token('NUMBER', num_str, start_line, start_column))
            continue

        # Literals: true, false, null
        literals = {
        'true': 'BOOLEAN', 
        'false': 'BOOLEAN', 
        'null': 'NULL'
        }
    
        for literal, token_type in literals.items():
            if input_string.startswith(literal, i):
                tokens.append(Token(token_type, literal, line, column))
                for _ in range(len(literal)):
                    advance()
                break
        else:
            # Check for invalid identifiers
            if char.isalpha():
                identifier = ''
                while i < length and (peek().isalnum() or peek() == '_'):
                    identifier += peek()
                    advance()
                raise LexerError(f"Invalid identifier: {identifier}", line, column)
            raise LexerError(f"Unexpected character: {char}", line, column)

    tokens.append(Token('EOF', '', line, column))
    return tokens
