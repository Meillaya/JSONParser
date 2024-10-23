import pytest
import time
import json
import random
import string
from src.lexer import lex, LexerError
from src.parser import Parser
from src.ast import parse_json, ast_to_json

def test_basic_json_parsing():
    # Test basic JSON types
    json_input = '''
    {
        "string": "Hello, World!",
        "number": 42,
        "float": 3.14,
        "boolean": true,
        "null": null,
        "array": [1, 2, 3],
        "object": {"nested": "value"}
    }
    '''
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    assert result["string"] == "Hello, World!"
    assert result["number"] == 42
    assert result["float"] == 3.14
    assert result["boolean"] is True
    assert result["null"] is None
    assert result["array"] == [1, 2, 3]
    assert result["object"] == {"nested": "value"}

def test_string_escapes():
    json_input = r'''
    {
        "escaped": "\"\\\/\b\f\n\r\t",
        "unicode": "\u0041\u0042\u0043",
        "special_chars": "Hello\n\tWorld!"
    }
    '''
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    assert result["escaped"] == "\"\\/\b\f\n\r\t"
    assert result["unicode"] == "ABC"
    assert result["special_chars"] == "Hello\n\tWorld!"

def test_nested_structures():
    json_input = '''
    {
        "nested": {
            "array": [
                {"key1": "value1"},
                {"key2": [1, 2, [3, 4, 5]]},
                {"key3": {"deep": {"deeper": null}}}
            ]
        }
    }
    '''
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    assert result["nested"]["array"][0] == {"key1": "value1"}
    assert result["nested"]["array"][1]["key2"] == [1, 2, [3, 4, 5]]
    assert result["nested"]["array"][2]["key3"]["deep"]["deeper"] is None

def test_number_formats():
    json_input = '''
    {
        "integer": 42,
        "negative": -123,
        "float": 3.14159,
        "exponent": 1.23e-4,
        "zero": 0,
        "neg_zero": -0
    }
    '''
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    assert result["integer"] == 42
    assert result["negative"] == -123
    assert pytest.approx(result["float"]) == 3.14159
    assert pytest.approx(result["exponent"]) == 1.23e-4
    assert result["zero"] == 0
    assert result["neg_zero"] == 0

def test_error_cases():
    # Test invalid JSON inputs
    invalid_inputs = [
        # Unclosed structures
        r'{"unclosed": "object"',
        r'["unclosed", "array"',
        
        # Invalid values
        r'{"invalid": undefined}',
        r'{"trailing": "comma",}',
        
        # Invalid numbers
        r'{"number": 01}',
        r'{"number": .123}',
        r'{"number": +123}',
        
        # Invalid strings
        r'{"string": "unterminated',
        r'{"string": "\u123"}',  # Invalid unicode escape
        
        # Control characters in strings
        r'{"control": "\x00"}',
        
        # Multiple values at root
        r'{"multiple": true} {"values": false}',
        
        # Missing colons and commas
        r'{"missing" "colon"}',
        r'{"missing": "comma" "next": "value"}'
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises((LexerError, ValueError)):
            tokens = lex(invalid_input)
            parser = Parser(tokens)
            parser.parse()

def test_roundtrip():
    # Test parsing and converting back to JSON
    original_json = '''
    {
        "string": "Hello, World!",
        "number": 42,
        "float": 3.14,
        "boolean": true,
        "null": null,
        "array": [1, 2, 3],
        "object": {"nested": "value"}
    }
    '''
    ast = parse_json(original_json)
    generated_json = ast_to_json(ast)
    reparsed_ast = parse_json(generated_json)
    
    assert ast.evaluate() == reparsed_ast.evaluate()

def test_empty_structures():
    json_input = '''
    {
        "empty_object": {},
        "empty_array": [],
        "empty_string": "",
        "array_with_empty": [{}, [], ""]
    }
    '''
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    assert result["empty_object"] == {}
    assert result["empty_array"] == []
    assert result["empty_string"] == ""
    assert result["array_with_empty"] == [{}, [], ""]

def test_whitespace_handling():
    # Test various whitespace combinations
    json_inputs = [
        '{"key":  "value"}',
        '{"key"\n:\r"value"\t}',
        '[ 1 , 2 , 3 ]',
        '{\n\n"key"\r\n:\t"value"\n}'
    ]
    
    for json_input in json_inputs:
        tokens = lex(json_input)
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast.evaluate() is not None
        
def test_complex_nested_structures():
    json_input = '''
    {
        "level1": {
            "level2": {
                "level3": {
                    "array": [
                        [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]],
                        {"obj": {"nested": {"deep": {"deeper": [1, 2, 3]}}}},
                        [{"a": 1}, {"b": 2}, {"c": [{"d": [{"e": null}]}]}]
                    ],
                    "mixed": [1, "string", true, null, {"key": [1, 2]}, [{"nested": null}]]
                }
            }
        }
    }
    '''
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    assert result["level1"]["level2"]["level3"]["array"][0][0][0] == [1, 2, 3]
    assert result["level1"]["level2"]["level3"]["array"][1]["obj"]["nested"]["deep"]["deeper"] == [1, 2, 3]
    assert result["level1"]["level2"]["level3"]["array"][2][2]["c"][0]["d"][0]["e"] is None

def test_large_array_performance():
    # Generate large array with 10000 elements
    large_array = list(range(10000))
    json_input = json.dumps({"large_array": large_array})
    
    start_time = time.time()
    tokens = lex(json_input)
    lex_time = time.time() - start_time
    
    start_time = time.time()
    parser = Parser(tokens)
    ast = parser.parse()
    parse_time = time.time() - start_time
    
    result = ast.evaluate()
    assert result["large_array"] == large_array
    assert lex_time < 1.0  # Lexing should take less than 1 second
    assert parse_time < 1.0  # Parsing should take less than 1 second

def test_deep_recursion():
    # Generate deeply nested object (100 levels)
    deep_obj = {}
    current = deep_obj
    for i in range(100):
        current["nested"] = {}
        current = current["nested"]
    current["value"] = "deep"
    
    json_input = json.dumps(deep_obj)
    tokens = lex(json_input)
    parser = Parser(tokens)
    ast = parser.parse()
    result = ast.evaluate()
    
    # Verify the deepest value
    current = result
    for _ in range(100):
        current = current["nested"]
    assert current["value"] == "deep"

def generate_random_json(depth=0, max_depth=5):
    if depth >= max_depth:
        return random.choice([
            random.randint(-1000, 1000),
            random.random(),
            ''.join(random.choices(string.ascii_letters, k=10)),
            True,
            False,
            None
        ])
    
    if random.random() < 0.5:
        return {
            ''.join(random.choices(string.ascii_letters, k=5)): generate_random_json(depth + 1, max_depth)
            for _ in range(random.randint(1, 5))
        }
    else:
        return [generate_random_json(depth + 1, max_depth) for _ in range(random.randint(1, 5))]

def test_random_json_structures():
    # Test 10 random complex JSON structures
    for _ in range(10):
        random_data = generate_random_json()
        json_input = json.dumps(random_data)
        
        tokens = lex(json_input)
        parser = Parser(tokens)
        ast = parser.parse()
        result = ast.evaluate()
        
        assert result == random_data

def test_benchmark_comparison():
    # Generate complex test data
    test_data = {
        "array": list(range(1000)),
        "nested": generate_random_json(max_depth=7),
        "strings": [''.join(random.choices(string.ascii_letters, k=20)) for _ in range(100)]
    }
    json_input = json.dumps(test_data)
    
    # Benchmark our parser
    start_time = time.time()
    our_result = parse_json(json_input).evaluate()
    our_time = time.time() - start_time
    
    # Benchmark Python's json parser
    start_time = time.time()
    stdlib_result = json.loads(json_input)
    stdlib_time = max(time.time() - start_time, 1e-10)  # Prevent division by zero
    
    # Verify results match
    assert our_result == stdlib_result
    
    # Log performance comparison
    print(f"\nPerformance comparison:")
    print(f"Our parser: {our_time:.4f} seconds")
    print(f"stdlib json: {stdlib_time:.4f} seconds")
    print(f"Ratio: {our_time/stdlib_time:.2f}x slower than stdlib")

def test_extreme_number_values():
    json_input = '''
    {
        "max_float": 1.7976931348623157e+308,
        "min_float": 2.2250738585072014e-308,
        "very_precise": 0.123456789012345678901234567890,
        "scientific": 1.23e+100,
        "negative_scientific": -4.56e-100
    }
    '''
    result = parse_json(json_input).evaluate()
    assert pytest.approx(result["max_float"]) == 1.7976931348623157e+308
    assert pytest.approx(result["min_float"]) == 2.2250738585072014e-308
    assert pytest.approx(result["scientific"]) == 1.23e+100
    assert pytest.approx(result["negative_scientific"]) == -4.56e-100

def test_unicode_edge_cases():
    json_input = '''
    {
        "emoji": "🌟🚀🌍",
        "chinese": "你好世界",
        "arabic": "مرحبا بالعالم",
        "mixed": "Hello世界🌟",
        "surrogate_pairs": "\uD83D\uDE00",
        "zero_width": "a\u200Bb",
        "rtl_mark": "\u200F\u200Etest"
    }
    '''
    result = parse_json(json_input).evaluate()
    assert result["emoji"] == "🌟🚀🌍"
    assert result["chinese"] == "你好世界"
    assert result["surrogate_pairs"] == "😀"

def test_stress_test_large_objects():
    # Generate large nested object with varied content
    large_obj = {
        str(i): {
            "array": list(range(100)),
            "string": "x" * 1000,
            "nested": {"a": i, "b": str(i), "c": [True, False, None] * 10}
        } for i in range(100)
    }
    json_input = json.dumps(large_obj)
    result = parse_json(json_input).evaluate()
    assert result == large_obj

def test_pathological_strings():
    json_input = '''
    {
        "backslashes": "\\\\\\\\\\\\",
        "quotes": "\\"\\"\\"\\"\\"",
        "mixed_escapes": "\\n\\t\\"\\\\\\b\\f\\r",
        "all_escapes": "\\u0000\\u0001\\u0002\\u0003",
        "repeated": "test test test test test test test test test test"
    }
    '''
    result = parse_json(json_input).evaluate()
    assert result["backslashes"] == "\\\\\\\\\\"
    assert result["quotes"] == '""""\"'

def test_nested_array_combinations():
    json_input = '''
    {
        "arrays": [
            [[[[[1]]]]], 
            [[], [[]], [[], [[]]]],
            [{"a": [1, {"b": [2, {"c": [3]}]}]}],
            [[null, [true, [false, [42, ["string"]]]]]],
            [[[[[[]]]]], [[[[[{}]]]]], [[[[[0]]]]]]
        ]
    }
    '''
    result = parse_json(json_input).evaluate()
    assert result["arrays"][0][0][0][0][0] == 1
    assert result["arrays"][2][0]["a"][1]["b"][1]["c"][0] == 3

def test_performance_edge_cases():
    # Test with alternating types in large array
    mixed_array = [
        item for _ in range(1000) 
        for item in [42, "string", True, None, {"key": "value"}, [1,2,3]]
    ]
    json_input = json.dumps({"mixed": mixed_array})
    
    start_time = time.time()
    result = parse_json(json_input).evaluate()
    parse_time = time.time() - start_time
    
    assert result["mixed"] == mixed_array
    assert parse_time < 2.0  # Should parse within reasonable time

def test_malformed_but_tricky_inputs():
    tricky_inputs = [
        '{"key": "value"}}',  # Extra closing brace
        '{"key": "value",}',  # Trailing comma
        '{"key": "value"}{',  # Multiple objects
        '[1,2,3,,4]',        # Double comma
        '{"a":1}"extra"',    # Extra content
        '{"a":1, b:2}',      # Unquoted key
    ]
    
    for input_str in tricky_inputs:
        with pytest.raises((LexerError, ValueError)):
            parse_json(input_str)

def test_boundary_whitespace():
    json_inputs = [
        '\n\n\n{"key": "value"}\n\n\n',
        '\t\t\t{"key": "value"}\t\t\t',
        ' ' * 1000 + '{"key": "value"}' + ' ' * 1000,
        '\r\n\r\n{"key": "value"}\r\n\r\n'
    ]
    
    for json_input in json_inputs:
        result = parse_json(json_input).evaluate()
        assert result == {"key": "value"}
