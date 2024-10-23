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

def parse_string(input_string: str, i: int, line: int, column: int) -> tuple[str, int, int]:
    value = ''
    start_column = column
    i += 1  # Skip opening quote
    
    while i < len(input_string):
        char = input_string[i]
        
        if char == '"':
            i += 1
            return value, i, column + 1
            
        if char == '\\':
            i += 1
            if i >= len(input_string):
                raise LexerError("Unterminated string literal", line, start_column)
                
            escape_char = input_string[i]
            escape_sequences = {
                '"': '"',
                '\\': '\\',
                '/': '/',
                'b': '\b',
                'f': '\f',
                'n': '\n',
                'r': '\r',
                't': '\t'
            }
            
            if escape_char in escape_sequences:
                value += escape_sequences[escape_char]
                column += 2  # Count both backslash and escape char
            elif escape_char == 'u':
                if i + 4 >= len(input_string):
                    raise LexerError("Invalid Unicode escape sequence", line, column)
                hex_str = input_string[i+1:i+5]
                if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                    raise LexerError(f"Invalid Unicode escape character: {hex_str}", line, column)
                value += chr(int(hex_str, 16))
                i += 4
                column += 6  # Count \u plus 4 hex digits
            else:
                raise LexerError(f"Invalid escape character: \\{escape_char}", line, column)
        else:
            value += char
            column += 1
        i += 1
    
    raise LexerError("Unterminated string literal", line, start_column)
    
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
        if char.isspace():
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
            string_value = ''
            advance()  # Skip opening quote
            
            while i < length and peek() != '"':
                if peek() == '\\':
                    advance()
                    if i >= length:
                        raise LexerError("Unterminated string", start_line, start_column)
                    
                    escape_char = peek()
                    escape_map = {
                        '"': '"',
                        '\\': '\\',
                        '/': '/',
                        'b': '\b',
                        'f': '\f',
                        'n': '\n',
                        'r': '\r',
                        't': '\t'
                    }
                    
                    if escape_char in escape_map:
                        string_value += escape_map[escape_char]
                        advance()
                    elif escape_char == 'u':
                        advance()
                        hex_str = ''
                        for _ in range(4):
                            if i >= length or peek() not in '0123456789abcdefABCDEF':
                                raise LexerError("Invalid Unicode escape sequence", line, column)
                            hex_str += peek()
                            advance()
                        string_value += chr(int(hex_str, 16))
                    else:
                        raise LexerError(f"Invalid escape character: \\{escape_char}", line, column)
                elif ord(peek()) < 0x20:
                    raise LexerError("Control characters not allowed in strings", line, column)
                else:
                    string_value += peek()
                    advance()
            
            if i >= length:
                raise LexerError("Unterminated string", start_line, start_column)
            advance()  # Skip closing quote
            tokens.append(Token('STRING', string_value, start_line, start_column))
            continue

        # Numbers
        if char == '-' or char.isdigit():
            start_line, start_column = line, column
            num_str = ''
            
            if char == '-':
                num_str += char
                advance()
                if not peek().isdigit():
                    raise LexerError("Invalid number format", start_line, start_column)
            
            if peek() == '0':
                num_str += peek()
                advance()
                if peek().isdigit():
                    raise LexerError("Numbers cannot have leading zeros", start_line, start_column)
            else:
                while i < length and peek().isdigit():
                    num_str += peek()
                    advance()
            
            if peek() == '.':
                num_str += peek()
                advance()
                if not peek().isdigit():
                    raise LexerError("Invalid number format", start_line, start_column)
                while i < length and peek().isdigit():
                    num_str += peek()
                    advance()
            
            if peek() in 'eE':
                num_str += peek()
                advance()
                if peek() in '+-':
                    num_str += peek()
                    advance()
                if not peek().isdigit():
                    raise LexerError("Invalid number format", start_line, start_column)
                while i < length and peek().isdigit():
                    num_str += peek()
                    advance()
            
            tokens.append(Token('NUMBER', num_str, start_line, start_column))
            continue

        # Literals
        literals = {
            'true': 'BOOLEAN',
            'false': 'BOOLEAN',
            'null': 'NULL'
        }
        
        matched = False
        for literal, token_type in literals.items():
            if input_string[i:].startswith(literal):
                tokens.append(Token(token_type, literal, line, column))
                for _ in range(len(literal)):
                    advance()
                matched = True
                break
        
        if matched:
            continue

        raise LexerError(f"Unexpected character: {char}", line, column)

    tokens.append(Token('EOF', '', line, column))
    return tokens


