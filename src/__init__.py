
from src.lexer import lex
from src.parser import Parser
from src.ast import ast_to_json

def parse_json_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        json_string = file.read()
    
    tokens = lex(json_string)
    parser = Parser(tokens)
    ast = parser.parse()
    
    return ast_to_json(ast)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python -m src <json_file_path>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    try:
        parsed_json = parse_json_file(json_file_path)
        print(parsed_json)
    except Exception as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
