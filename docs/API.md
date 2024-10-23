# JSON Parser API Documentation

## Overview
A robust JSON parser implementation that supports parsing JSON strings into Python objects with full support for all JSON data types, Unicode characters, and nested structures.

## Core Components

### Lexer
The lexer converts JSON text into a sequence of tokens.

```python
from src.lexer import lex, Token, LexerError
```

# Basic usage

tokens = lex('{"name": "John"}')

### Token Class

type: Token type (STRING, NUMBER, BOOLEAN, etc.)
value: Actual token value
line: Line number in source
column: Column number in sourc

### Parser
Converts tokens into an Abstract Syntax Tree (AST)

```python
from src.parser import Parser, parse

# Using Parser class directly
tokens = lex(json_string)
parser = Parser(tokens)
ast = parser.parse()

# Using convenience function
ast = parse(json_string)

```

### AST Nodes
Represents JSON data structures in memory.

``` python
from src.ast import (
    ObjectNode,
    ArrayNode,
    StringNode,
    NumberNode,
    BooleanNode,
    NullNode
)
```

# Usage Examples
Basic Parsing

``from src.parser import parse``

## Parse simple JSON

```json_str = '{"name": "John", "age": 30}'
result = parse(json_str)
data = result.evaluate()
```

## Handling Complex Structures

### Nested objects and arrays
``` python
json_str = '''
{
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "settings": {
        "theme": "dark",
        "notifications": true
    }
}
'''
result = parse(json_str)
data = result.evaluate()
```

## Unicode Support

### Unicode characters and escape sequences
``` python
json_str = '{"message": "Hello \\u2665 World!"}'
result = parse(json_str)
data = result.evaluate()  # Contains heart symbol
```

## Error Handling

```python
try:
    result = parse(invalid_json)
except LexerError as e:
    print(f"Lexer error at line {e.line}, column {e.column}")
except ValueError as e:
    print(f"Parser error: {str(e)}")
```

# Features

## Supported Data Types

- Objects ({})
- Arrays ([])
- Strings ("...")
- Numbers (integer, float, scientific notation)
- Booleans (true, false)
- Null (null)


## Number Format Support


- Integers: 42, -17
- Floating point: 3.14159
- Scientific notation: 1.23e+2, 4.56e-3
- Zero: 0, 0.0

## String Features

- Unicode escape sequences: \u0000 to \uFFFF
- Standard escape sequences: ", \, /, \b, \f, \n, \r, \t
- Raw Unicode characters

## Special Features

- Detailed error reporting with line and column information
- Handling of whitespace and formatting
- Support for deeply nested structures
- Duplicate key handling (last value wins)
- Large number support
- Performance optimized for large JSON files

## Error Handling

### LexerError

Raised for invalid token sequences with location information:

- Invalid characters
- Malformed strings
- Invalid escape sequences
- Invalid number formats

### ValueError

Raised for structural JSON errors:

- Unclosed objects/arrays
- Missing commas/colons
- Invalid value types
- Unexpected tokens


## Best Practices

Always use error handling when parsing untrusted input
For large files, consider streaming approaches
Validate expected structure after parsing
Use the high-level parse() function for simple cases
Use Parser class directly for more control

## Performance Considerations

Parser handles nested structures up to system recursion limit
Memory usage proportional to input size
Efficient string and number handling
Optimized token generation