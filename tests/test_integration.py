
import unittest
import json
from src import parse_json, JSONParseError

class TestJSONParser(unittest.TestCase):
    def test_simple_object(self):
        input_json = '{"key": "value"}'
        expected = {"key": "value"}
        self.assertEqual(parse_json(input_json), expected)

    def test_nested_object(self):
        input_json = '{"outer": {"inner": "value"}}'
        expected = {"outer": {"inner": "value"}}
        self.assertEqual(parse_json(input_json), expected)

    def test_array(self):
        input_json = '[1, 2, 3]'
        expected = [1, 2, 3]
        self.assertEqual(parse_json(input_json), expected)

    def test_complex_nested_structure(self):
        input_json = '''
        {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "country": "USA"
            },
            "phoneNumbers": [
                {"type": "home", "number": "555-1234"},
                {"type": "work", "number": "555-5678"}
            ],
            "isStudent": false,
            "grades": null
        }
        '''
        expected = {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "country": "USA"
            },
            "phoneNumbers": [
                {"type": "home", "number": "555-1234"},
                {"type": "work", "number": "555-5678"}
            ],
            "isStudent": False,
            "grades": None
        }
        self.assertEqual(parse_json(input_json), expected)

    def test_empty_object(self):
        input_json = '{}'
        expected = {}
        self.assertEqual(parse_json(input_json), expected)

    def test_empty_array(self):
        input_json = '[]'
        expected = []
        self.assertEqual(parse_json(input_json), expected)

    def test_unicode_characters(self):
        input_json = '{"unicode": "\\u00A9 2023"}'
        expected = {"unicode": "© 2023"}
        self.assertEqual(parse_json(input_json), expected)

    def test_escaped_characters(self):
        input_json = '{"escaped": "This is a \\"quoted\\" string with a \\\\ backslash"}'
        expected = {"escaped": 'This is a "quoted" string with a \\ backslash'}
        self.assertEqual(parse_json(input_json), expected)

    def test_large_numbers(self):
        input_json = '{"large_int": 1234567890123456789, "large_float": 1.23456789e+20}'
        expected = {"large_int": 1234567890123456789, "large_float": 1.23456789e+20}
        self.assertEqual(parse_json(input_json), expected)
        
    def test_escaped_characters_and_unicode(self):
        input_json = r'''
        {
            "escaped_chars": "\"\\\/\b\f\n\r\t",
            "unicode": "\u00A9 \u2665 \u{1F600}",
            "mixed": "Hello,\nWorld! \u263A"
        }
        '''
        expected = {
            "escaped_chars": "\"\\/\b\f\n\r\t",
            "unicode": "© ♥ 😀",
            "mixed": "Hello,\nWorld! ☺"
        }
        self.assertEqual(parse_json(input_json), expected)
    
    def test_various_number_formats(self):
        input_json = '''
        {
            "integer": 42,
            "negative": -17,
            "float": 3.14159,
            "exponent_positive": 1.23e+2,
            "exponent_negative": 4.56e-3,
            "zero": 0,
            "leading_zero": 0.123
        }
        '''
        expected = {
            "integer": 42,
            "negative": -17,
            "float": 3.14159,
            "exponent_positive": 123.0,
            "exponent_negative": 0.00456,
            "zero": 0,
            "leading_zero": 0.123
        }
        self.assertEqual(parse_json(input_json), expected)
        
    def test_complex_nested_structure_with_mixed_types(self):
        input_json = '''
        {
            "data": [
                {
                    "id": 1,
                    "info": {
                        "name": "John Doe",
                        "age": 30,
                        "skills": ["Python", "JSON", null],
                        "address": {
                            "street": "123 Main St",
                            "city": "Anytown",
                            "coordinates": [40.7128, -74.0060]
                        }
                    },
                    "active": true
                },
                {
                    "id": 2,
                    "info": null,
                    "active": false
                }
            ],
            "metadata": {
                "total_count": 2,
                "page": 1,
                "limit": 10
            }
        }
        '''
        expected = {
            "data": [
                {
                    "id": 1,
                    "info": {
                        "name": "John Doe",
                        "age": 30,
                        "skills": ["Python", "JSON", None],
                        "address": {
                            "street": "123 Main St",
                            "city": "Anytown",
                            "coordinates": [40.7128, -74.0060]
                        }
                    },
                    "active": True
                },
                {
                    "id": 2,
                    "info": None,
                    "active": False
                }
            ],
            "metadata": {
                "total_count": 2,
                "page": 1,
                "limit": 10
            }
        }
        self.assertEqual(parse_json(input_json), expected)

    def test_deeply_nested_structure(self):
        input_json = '{"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}'
        expected = {"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}
        self.assertEqual(parse_json(input_json), expected)

    def test_array_with_mixed_types(self):
        input_json = '[1, "two", true, null, {"key": "value"}, [1, 2, 3]]'
        expected = [1, "two", True, None, {"key": "value"}, [1, 2, 3]]
        self.assertEqual(parse_json(input_json), expected)

    def test_whitespace_handling(self):
        input_json = '''
        {
            "key1" :   "value1"   ,
            "key2":      42,
            "key3"    :[  1 ,    2,   3    ]
        }
        '''
        expected = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        self.assertEqual(parse_json(input_json), expected)

    def test_invalid_json(self):
        invalid_inputs = [
            '{',
            '}',
            '[',
            ']',
            '{"key": }',
            '{"key": "value",}',
            '[1, 2, 3,]',
            '{"a": 1, "a": 2}',
            '"unclosed string',
            '{"key": undefined}',
        ]
        for invalid_json in invalid_inputs:
            with self.assertRaises(JSONParseError):
                parse_json(invalid_json)
    
    def test_large_complex_json(self):
    # Generate a large, complex JSON structure
        import random
        import string

        def generate_complex_item(depth=0):
            if depth > 5:
                return random.choice([
                    random.randint(-1000, 1000),
                    random.uniform(-1000, 1000),
                    ''.join(random.choices(string.ascii_letters, k=10)),
                    None,
                    True,
                    False
                ])
            
            if random.random() < 0.5:
                return {
                    ''.join(random.choices(string.ascii_lowercase, k=5)): generate_complex_item(depth + 1)
                    for _ in range(random.randint(1, 5))
                }
            else:
                return [generate_complex_item(depth + 1) for _ in range(random.randint(1, 5))]

        large_complex_json = {
            "data": [generate_complex_item() for _ in range(100)],
            "metadata": {
                "timestamp": "2023-04-15T12:00:00Z",
                "version": "1.0.0",
                "checksum": "".join(random.choices(string.hexdigits, k=32))
            }
        }

        input_json = json.dumps(large_complex_json)
        self.assertEqual(parse_json(input_json), large_complex_json)


    def test_performance_large_file(self):
        # Generate a large JSON file
        large_json = {
            "data": [{"id": i, "value": f"item{i}"} for i in range(10000)]
        }
        large_json_str = json.dumps(large_json)

        # Test parsing performance
        import time
        start_time = time.time()
        parsed_json = parse_json(large_json_str)
        end_time = time.time()

        self.assertEqual(parsed_json, large_json)
        self.assertLess(end_time - start_time, 1.0)  # Ensure parsing takes less than 1 second

if __name__ == '__main__':
    unittest.main()
