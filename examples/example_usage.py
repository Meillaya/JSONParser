from src.lexer import lex
from src.parser import Parser
from src.ast import ObjectNode, ArrayNode

def basic_usage():
    # Simple object parsing
    json_str = '{"name": "John", "age": 30}'
    tokens = lex(json_str)
    parser = Parser(tokens)
    result = parser.parse()
    print("Basic object:", result.evaluate())

def array_usage():
    # Array with mixed types
    json_str = '[1, "two", true, null, {"key": "value"}]'
    tokens = lex(json_str)
    parser = Parser(tokens)
    result = parser.parse()
    print("Mixed array:", result.evaluate())

def nested_structures():
    # Complex nested structure
    json_str = '''
    {
        "user": {
            "profile": {
                "name": "Alice",
                "contacts": [
                    {"type": "email", "value": "alice@example.com"},
                    {"type": "phone", "value": "555-0123"}
                ]
            },
            "settings": {
                "theme": "dark",
                "notifications": true
            }
        }
    }
    '''
    tokens = lex(json_str)
    parser = Parser(tokens)
    result = parser.parse()
    print("Nested structure:", result.evaluate())

def unicode_example():
    # Unicode and special characters
    json_str = '{"message": "Hello \\u2665 World! \\n Special \\t chars"}'
    tokens = lex(json_str)
    parser = Parser(tokens)
    result = parser.parse()
    print("Unicode string:", result.evaluate())

def number_formats():
    # Various number formats
    json_str = '''
    {
        "integer": 42,
        "negative": -17,
        "float": 3.14159,
        "scientific": 1.23e-4
    }
    '''
    tokens = lex(json_str)
    parser = Parser(tokens)
    result = parser.parse()
    print("Number formats:", result.evaluate())

def main():
    print("JSON Parser Examples\n")
    
    print("1. Basic Usage:")
    basic_usage()
    print()
    
    print("2. Array Usage:")
    array_usage()
    print()
    
    print("3. Nested Structures:")
    nested_structures()
    print()
    
    print("4. Unicode Handling:")
    unicode_example()
    print()
    
    print("5. Number Formats:")
    number_formats()

if __name__ == "__main__":
    main()
