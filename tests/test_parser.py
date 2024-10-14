
import unittest
from src.parser import parse
from src.ast import ObjectNode, ArrayNode, StringNode, NumberNode, BooleanNode, NullNode

class TestParser(unittest.TestCase):
    def test_parse_empty_object(self):
        result = parse("{}")
        self.assertIsInstance(result, ObjectNode)
        self.assertEqual(len(result.pairs), 0)

    def test_parse_simple_object(self):
        result = parse('{"key": "value"}')
        self.assertIsInstance(result, ObjectNode)
        self.assertEqual(len(result.pairs), 1)
        self.assertIsInstance(result.pairs["key"], StringNode)
        self.assertEqual(result.pairs["key"].value, "value")

    def test_parse_nested_object(self):
        result = parse('{"outer": {"inner": 42}}')
        self.assertIsInstance(result, ObjectNode)
        self.assertIsInstance(result.pairs["outer"], ObjectNode)
        self.assertIsInstance(result.pairs["outer"].pairs["inner"], NumberNode)
        self.assertEqual(result.pairs["outer"].pairs["inner"].value, 42)

    def test_parse_empty_array(self):
        result = parse("[]")
        self.assertIsInstance(result, ArrayNode)
        self.assertEqual(len(result.elements), 0)

    def test_parse_simple_array(self):
        result = parse('[1, "two", true]')
        self.assertIsInstance(result, ArrayNode)
        self.assertEqual(len(result.elements), 3)
        self.assertIsInstance(result.elements[0], NumberNode)
        self.assertIsInstance(result.elements[1], StringNode)
        self.assertIsInstance(result.elements[2], BooleanNode)

    def test_parse_nested_array(self):
        result = parse('[[1, 2], [3, 4]]')
        self.assertIsInstance(result, ArrayNode)
        self.assertEqual(len(result.elements), 2)
        self.assertIsInstance(result.elements[0], ArrayNode)
        self.assertIsInstance(result.elements[1], ArrayNode)

    def test_parse_string(self):
        result = parse('"hello"')
        self.assertIsInstance(result, StringNode)
        self.assertEqual(result.value, "hello")

    def test_parse_number(self):
        result = parse('42.5')
        self.assertIsInstance(result, NumberNode)
        self.assertEqual(result.value, 42.5)

    def test_parse_boolean(self):
        result_true = parse('true')
        self.assertIsInstance(result_true, BooleanNode)
        self.assertTrue(result_true.value)

        result_false = parse('false')
        self.assertIsInstance(result_false, BooleanNode)
        self.assertFalse(result_false.value)

    def test_parse_null(self):
        result = parse('null')
        self.assertIsInstance(result, NullNode)

    def test_parse_complex_json(self):
        json_str = '''
        {
            "name": "John Doe",
            "age": 30,
            "isStudent": false,
            "grades": [85, 90, 92],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zipcode": "12345"
            },
            "hobbies": ["reading", "swimming", null]
        }
        '''
        result = parse(json_str)
        self.assertIsInstance(result, ObjectNode)
        self.assertEqual(len(result.pairs), 6)
        self.assertIsInstance(result.pairs["name"], StringNode)
        self.assertIsInstance(result.pairs["age"], NumberNode)
        self.assertIsInstance(result.pairs["isStudent"], BooleanNode)
        self.assertIsInstance(result.pairs["grades"], ArrayNode)
        self.assertIsInstance(result.pairs["address"], ObjectNode)
        self.assertIsInstance(result.pairs["hobbies"], ArrayNode)
        self.assertIsInstance(result.pairs["hobbies"].elements[2], NullNode)

    def test_parse_invalid_json(self):
        with self.assertRaises(ValueError):
            parse('{')

        with self.assertRaises(ValueError):
            parse('{"key": }')

        with self.assertRaises(ValueError):
            parse('[1, 2,]')

if __name__ == '__main__':
    unittest.main()
