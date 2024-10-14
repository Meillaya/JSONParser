
from typing import List
from src.lexer import Token, lex
from src.ast import ASTNode, ObjectNode, ArrayNode, StringNode, NumberNode, BooleanNode, NullNode

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ASTNode:
        return self.parse_value()

    def parse_value(self) -> ASTNode:
        token = self.current_token()
        if token.type == 'LEFT_BRACE':
            return self.parse_object()
        elif token.type == 'LEFT_BRACKET':
            return self.parse_array()
        elif token.type == 'STRING':
            self.advance()
            return StringNode(token.value[1:-1])  # Remove quotes
        elif token.type == 'NUMBER':
            self.advance()
            return NumberNode(float(token.value))
        elif token.type == 'BOOLEAN':
            self.advance()
            return BooleanNode(token.value == 'true')
        elif token.type == 'NULL':
            self.advance()
            return NullNode()
        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_object(self) -> ObjectNode:
        self.consume('LEFT_BRACE')
        pairs = {}
        if self.current_token().type != 'RIGHT_BRACE':
            while True:
                key = self.consume('STRING').value[1:-1]  # Remove quotes
                self.consume('COLON')
                value = self.parse_value()
                pairs[key] = value
                if self.current_token().type != 'COMMA':
                    break
                self.advance()
        self.consume('RIGHT_BRACE')
        return ObjectNode(pairs)

    def parse_array(self) -> ArrayNode:
        self.consume('LEFT_BRACKET')
        elements = []
        if self.current_token().type != 'RIGHT_BRACKET':
            while True:
                element = self.parse_value()
                elements.append(element)
                if self.current_token().type != 'COMMA':
                    break
                self.advance()
        self.consume('RIGHT_BRACKET')
        return ArrayNode(elements)

    def current_token(self) -> Token:
        return self.tokens[self.current]

    def advance(self):
        self.current += 1

    def consume(self, expected_type: str) -> Token:
        if self.current_token().type == expected_type:
            token = self.current_token()
            self.advance()
            return token
        else:
            raise ValueError(f"Expected {expected_type}, but got {self.current_token().type}")

def parse(input_string: str) -> ASTNode:
    tokens = lex(input_string)
    parser = Parser(tokens)
    return parser.parse()
