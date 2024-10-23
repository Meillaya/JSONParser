
from typing import List
from src.lexer import Token, lex
from src.ast import ASTNode, ObjectNode, ArrayNode, StringNode, NumberNode, BooleanNode, NullNode

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ASTNode:
        value = self.parse_value()
        if self.current < len(self.tokens) - 1:  # -1 for EOF token
            raise ValueError("Unexpected tokens after parsing completed")
        return value

    def parse_value(self) -> ASTNode:
        token = self.current_token()
        
        if token.type == 'LEFT_BRACE':
            return self.parse_object()
        elif token.type == 'LEFT_BRACKET':
            return self.parse_array()
        elif token.type == 'STRING':
            self.advance()
            return StringNode(token.value)
        elif token.type == 'NUMBER':
            self.advance()
            try:
                return NumberNode(float(token.value))
            except ValueError:
                raise ValueError(f"Invalid number format: {token.value}")
        elif token.type == 'BOOLEAN':
            self.advance()
            return BooleanNode(token.value == 'true')
        elif token.type == 'NULL':
            self.advance()
            return NullNode()
        else:
            raise ValueError(f"Unexpected token: {token.type}")

    def parse_object(self) -> ObjectNode:
        self.consume('LEFT_BRACE')
        pairs = {}
        
        if self.current_token().type != 'RIGHT_BRACE':
            while True:
                if self.current_token().type == 'EOF':
                    raise ValueError("Unclosed object: expected '}'")
                    
                if self.current_token().type != 'STRING':
                    raise ValueError("Expected string key in object")
                
                key = self.consume('STRING').value
                self.consume('COLON')
                value = self.parse_value()
                pairs[key] = value
                
                if self.current_token().type == 'RIGHT_BRACE':
                    break
                    
                self.consume('COMMA')
        
        self.consume('RIGHT_BRACE')
        return ObjectNode(pairs)

    def parse_array(self) -> ArrayNode:
        self.consume('LEFT_BRACKET')
        elements = []
        
        if self.current_token().type != 'RIGHT_BRACKET':
            while True:
                if self.current_token().type == 'EOF':
                    raise ValueError("Unclosed array: expected ']'")
                    
                elements.append(self.parse_value())
                
                if self.current_token().type == 'RIGHT_BRACKET':
                    break
                    
                self.consume('COMMA')
        
        self.consume('RIGHT_BRACKET')
        return ArrayNode(elements)

    def current_token(self) -> Token:
        if self.current >= len(self.tokens):
            raise IndexError("Unexpected end of input")
        return self.tokens[self.current]

    def advance(self) -> None:
        self.current += 1

    def consume(self, expected_type: str) -> Token:
        token = self.current_token()
        if token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, but got {token.type}")
        self.advance()
        return token
