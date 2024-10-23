
import json
from typing import Any, Dict, List, Union

class ASTNode:
    def evaluate(self) -> Any:
        raise NotImplementedError

class ObjectNode(ASTNode):
    def __init__(self, pairs: Dict[str, ASTNode]):
        self.pairs = pairs

    def evaluate(self) -> Dict:
        return {key: value.evaluate() for key, value in self.pairs.items()}

class ArrayNode(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements

    def evaluate(self) -> List:
        return [element.evaluate() for element in self.elements]

class StringNode(ASTNode):
    def __init__(self, value: str):
        self.value = value

    def evaluate(self) -> str:
        return self.value

class NumberNode(ASTNode):
    def __init__(self, value: Union[int, float]):
        self.value = value

    def evaluate(self) -> Union[int, float]:
        return self.value

class BooleanNode(ASTNode):
    def __init__(self, value: bool):
        self.value = value

    def evaluate(self) -> bool:
        return self.value

class NullNode(ASTNode):
    def evaluate(self) -> None:
        return None

def parse_json(json_string: str) -> ASTNode:
    def parse_value(value: Any) -> ASTNode:
        if isinstance(value, dict):
            return ObjectNode({k: parse_value(v) for k, v in value.items()})
        elif isinstance(value, list):
            return ArrayNode([parse_value(item) for item in value])
        elif isinstance(value, str):
            return StringNode(value)
        elif isinstance(value, (int, float)):
            return NumberNode(value)
        elif isinstance(value, bool):
            return BooleanNode(value)
        elif value is None:
            return NullNode()
        else:
            raise ValueError(f"Unsupported JSON value: {value}")

    parsed_json = json.loads(json_string)
    return parse_value(parsed_json)

def ast_to_json(node: ASTNode) -> str:
    def to_json_value(node: ASTNode) -> Any:
        if isinstance(node, ObjectNode):
            return {k: to_json_value(v) for k, v in node.pairs.items()}
        elif isinstance(node, ArrayNode):
            return [to_json_value(item) for item in node.elements]
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, BooleanNode):
            return node.value
        elif isinstance(node, NullNode):
            return None
        else:
            raise ValueError(f"Unsupported AST node: {node}")

    return json.dumps(to_json_value(node), indent=2)
