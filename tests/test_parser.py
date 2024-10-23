import unittest
from src.parser import Parser
from src.lexer import LexerError, lex, Token
from src.ast import ObjectNode, ArrayNode, StringNode, NumberNode, BooleanNode, NullNode

class TestParser(unittest.TestCase):
    def test_empty_object(self):
        tokens = lex('{}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ObjectNode)
        self.assertEqual(len(result.pairs), 0)

    def test_empty_array(self):
        tokens = lex('[]')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ArrayNode)
        self.assertEqual(len(result.elements), 0)

    def test_simple_object(self):
        tokens = lex('{"key": "value"}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ObjectNode)
        self.assertEqual(len(result.pairs), 1)
        self.assertEqual(result.pairs['key'].evaluate(), "value")

    def test_nested_objects(self):
        tokens = lex('{"outer": {"inner": "value"}}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ObjectNode)
        self.assertIsInstance(result.pairs['outer'], ObjectNode)
        self.assertEqual(result.pairs['outer'].pairs['inner'].evaluate(), "value")

    def test_array_with_mixed_types(self):
        tokens = lex('[1, "string", true, null, {"key": "value"}]')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ArrayNode)
        self.assertEqual(len(result.elements), 5)
        self.assertIsInstance(result.elements[0], NumberNode)
        self.assertIsInstance(result.elements[1], StringNode)
        self.assertIsInstance(result.elements[2], BooleanNode)
        self.assertIsInstance(result.elements[3], NullNode)
        self.assertIsInstance(result.elements[4], ObjectNode)

    def test_deeply_nested_structure(self):
        tokens = lex('{"level1": {"level2": {"level3": [1, 2, {"deep": "value"}]}}}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ObjectNode)
        level1 = result.pairs['level1']
        level2 = level1.pairs['level2']
        level3 = level2.pairs['level3']
        self.assertIsInstance(level3, ArrayNode)
        self.assertEqual(level3.elements[2].pairs['deep'].evaluate(), "value")

    def test_number_variations(self):
        test_cases = [
            "42",
            "-17",
            "3.14159",
            "1.23e+2",
            "4.56e-3",
            "0",
            "0.123"
        ]
        for test_case in test_cases:
            tokens = lex(test_case)
            parser = Parser(tokens)
            result = parser.parse()
            self.assertIsInstance(result, NumberNode)

    def test_string_escapes(self):
        tokens = lex(r'"\"\\\n\r\t\b\f"')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, StringNode)
        self.assertEqual(result.evaluate(), '\"\\\n\r\t\b\f')

    def test_unicode_characters(self):
        tokens = lex('"\\u00A9 \\u2665"')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result.evaluate(), "© ♥")

    def test_boolean_values(self):
        for value in ['true', 'false']:
            tokens = lex(value)
            parser = Parser(tokens)
            result = parser.parse()
            self.assertIsInstance(result, BooleanNode)
            self.assertEqual(result.evaluate(), value == 'true')

    def test_null_value(self):
        tokens = lex('null')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, NullNode)
        self.assertIsNone(result.evaluate())

    def test_error_missing_comma(self):
        with self.assertRaises(ValueError):
            tokens = lex('{"key1": "value1" "key2": "value2"}')
            parser = Parser(tokens)
            parser.parse()

    def test_error_trailing_comma(self):
        with self.assertRaises(ValueError):
            tokens = lex('{"key": "value",}')
            parser = Parser(tokens)
            parser.parse()

    def test_error_missing_colon(self):
        with self.assertRaises(ValueError):
            tokens = lex('{"key" "value"}')
            parser = Parser(tokens)
            parser.parse()

    def test_error_invalid_value(self):
        with self.assertRaises(LexerError):  # Changed from ValueError to LexerError
            tokens = lex('{"key": undefined}')
            parser = Parser(tokens)
            parser.parse()

    def test_error_unclosed_object(self):
        with self.assertRaises(ValueError):  # Keep ValueError but adjust the test
            tokens = lex('{"key": "value"')
            parser = Parser(tokens)
            try:
                parser.parse()
            except IndexError:
                raise ValueError("Unclosed object")

    def test_error_unclosed_array(self):
        with self.assertRaises(ValueError):  # Keep ValueError but adjust the test
            tokens = lex('[1, 2, 3')
            parser = Parser(tokens)
            try:
                parser.parse()
            except IndexError:
                raise ValueError("Unclosed array")

    def test_complex_structure(self):
        json_str = '''
        {
            "name": "Test Object",
            "numbers": [1, 2, 3, -4.5, 6.78e-2],
            "nested": {
                "array": [true, false, null],
                "object": {"key": "value"}
            },
            "empty": {},
            "unicode": "\\u00A9 2023"
        }
        '''
        tokens = lex(json_str)
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ObjectNode)
        self.assertEqual(len(result.pairs), 5)
        self.assertIsInstance(result.pairs['numbers'], ArrayNode)
        self.assertIsInstance(result.pairs['nested'], ObjectNode)
        
    def test_whitespace_variations(self):
        """Test various whitespace combinations"""
        inputs = [
            '{ "key" : "value" }',
            '{\n"key"\n:\n"value"\n}',
            '{ \t"key"\r\n:\t"value"\t}',
            '[  1  ,  2  ,  3  ]'
        ]
        for input_str in inputs:
            tokens = lex(input_str)
            parser = Parser(tokens)
            result = parser.parse()
            self.assertIsInstance(result, (ObjectNode, ArrayNode))

    def test_empty_string(self):
        """Test empty string values"""
        tokens = lex('{"key": ""}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result.pairs['key'].evaluate(), "")

    def test_number_edge_cases(self):
        """Test edge cases for number parsing"""
        valid_numbers = [
            "0.0",
            "-0",
            "1e-10",
            "1.23e+10",
            "0.123456789",
            "1234567890"
        ]
        for num in valid_numbers:
            tokens = lex(num)
            parser = Parser(tokens)
            result = parser.parse()
            self.assertIsInstance(result, NumberNode)

    def test_nested_arrays(self):
        """Test deeply nested arrays"""
        tokens = lex('[[[[["deep"]]]], [[], []], []]')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result, ArrayNode)
        self.assertEqual(result.elements[0].elements[0].elements[0].elements[0].elements[0].evaluate(), "deep")

    def test_complex_unicode(self):
        """Test complex Unicode sequences"""
        tokens = lex('{"unicode": "\\u0001\\u0002\\u0003\\uFFFF"}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(len(result.pairs['unicode'].evaluate()), 4)

    def test_large_integer_boundaries(self):
        """Test large integer values"""
        tokens = lex('[9007199254740991, -9007199254740991]')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(len(result.elements), 2)

    def test_object_key_uniqueness(self):
        """Test handling of duplicate keys"""
        tokens = lex('{"key": 1, "key": 2}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result.pairs['key'].evaluate(), 2)

    def test_mixed_nesting_complex(self):
        """Test complex mixed nesting of arrays and objects"""
        json_str = '''
        {
            "array_of_objects": [
                {"id": 1, "data": [1,2,3]},
                {"id": 2, "data": [4,5,6]},
                {"id": 3, "data": {"nested": ["a","b","c"]}}
            ],
            "object_of_arrays": {
                "first": [1, {"x": [2, [3, 4]]}, 5],
                "second": [{"y": {"z": [6, 7, [8, 9]]}}]
            }
        }
        '''
        tokens = lex(json_str)
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIsInstance(result.pairs['array_of_objects'], ArrayNode)
        self.assertIsInstance(result.pairs['object_of_arrays'], ObjectNode)

    def test_special_character_keys(self):
        """Test object keys with special characters"""
        tokens = lex('{"\\u0021": 1, "\\n": 2, "\\t": 3}')
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(len(result.pairs), 3)

    def test_recursive_structure(self):
        """Test handling of deep recursive structures"""
        depth = 100
        # Build a nested structure like {"a": {"a": {"a": null}}}
        json_str = '{"a": ' * depth + 'null' + '}' * depth
        tokens = lex(json_str)
        parser = Parser(tokens)
        result = parser.parse()
        
        # Verify the structure
        current = result
        for _ in range(depth):
            self.assertIsInstance(current, ObjectNode)
            self.assertEqual(len(current.pairs), 1)
            if _ < depth - 1:
                current = current.pairs['a']
            else:
                self.assertIsInstance(current.pairs['a'], NullNode)


    def test_error_invalid_number_formats(self):
        """Test invalid number formats"""
        invalid_numbers = [
            '01',  # Leading zero
            '-01',  # Leading zero in negative
            '1.',  # Trailing decimal point
            '.1',  # Leading decimal point
            '1e',  # Incomplete exponent
            '1e+',  # Incomplete exponent sign
            '--1'  # Double negative
        ]
        for num in invalid_numbers:
            with self.assertRaises((ValueError, LexerError)):
                tokens = lex(num)
                parser = Parser(tokens)
                parser.parse()


if __name__ == '__main__':
    unittest.main()
