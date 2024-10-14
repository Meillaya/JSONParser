import unittest
from src.lexer import lex, Token

class TestLexer(unittest.TestCase):

    def test_empty_input(self):
        tokens = lex("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token('EOF', '', 1, 1))

    def test_whitespace_only(self):
        tokens = lex("   \t  \n  ")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], Token('EOF', '', 2, 3))

    def test_simple_object(self):
        input_string = '{"key": "value"}'
        expected_tokens = [
            Token('LEFT_BRACE', '{', 1, 1),
            Token('STRING', '"key"', 1, 2),
            Token('COLON', ':', 1, 7),
            Token('STRING', '"value"', 1, 9),
            Token('RIGHT_BRACE', '}', 1, 16),
            Token('EOF', '', 1, 17)
        ]
        self.assertEqual(lex(input_string), expected_tokens)

    def test_simple_array(self):
        input_string = '[1, 2, 3]'
        expected_tokens = [
            Token('LEFT_BRACKET', '[', 1, 1),
            Token('NUMBER', '1', 1, 2),
            Token('COMMA', ',', 1, 3),
            Token('NUMBER', '2', 1, 5),
            Token('COMMA', ',', 1, 6),
            Token('NUMBER', '3', 1, 8),
            Token('RIGHT_BRACKET', ']', 1, 9),
            Token('EOF', '', 1, 10)
        ]
        self.assertEqual(lex(input_string), expected_tokens)

    def test_nested_structure(self):
        input_string = '{"array": [1, {"nested": true}, null]}'
        expected_tokens = [
            Token('LEFT_BRACE', '{', 1, 1),
            Token('STRING', '"array"', 1, 2),
            Token('COLON', ':', 1, 9),
            Token('LEFT_BRACKET', '[', 1, 11),
            Token('NUMBER', '1', 1, 12),
            Token('COMMA', ',', 1, 13),
            Token('LEFT_BRACE', '{', 1, 15),
            Token('STRING', '"nested"', 1, 16),
            Token('COLON', ':', 1, 24),
            Token('TRUE', 'true', 1, 26),
            Token('RIGHT_BRACE', '}', 1, 30),
            Token('COMMA', ',', 1, 31),
            Token('NULL', 'null', 1, 33),
            Token('RIGHT_BRACKET', ']', 1, 37),
            Token('RIGHT_BRACE', '}', 1, 38),
            Token('EOF', '', 1, 39)
        ]
        self.assertEqual(lex(input_string), expected_tokens)

    def test_string_with_escapes(self):
        input_string = r'"This is a \"test\" string with \\ escapes\n and unicode \u1234"'
        tokens = lex(input_string)
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, 'STRING')
        self.assertEqual(tokens[0].value, input_string)
        self.assertEqual(tokens[1].type, 'EOF')

    def test_string_with_all_escape_characters(self):
        input_string = r'"\"\b\f\n\r\t\\\/"'
        expected_value = '"\"\b\f\n\r\t\\\/"'
        tokens = lex(input_string)
        self.assertEqual(tokens[0].type, 'STRING')
        self.assertEqual(tokens[0].value, expected_value)

    def test_numbers(self):
        input_string = '[-123, 0, 3.1415, 6.022e23, -2.71828]'
        tokens = lex(input_string)
        expected_values = ['[', '-123', ',', '0', ',', '3.1415', ',', '6.022e23', ',', '-2.71828', ']']
        expected_types = ['LEFT_BRACKET', 'NUMBER', 'COMMA', 'NUMBER', 'COMMA', 'NUMBER', 'COMMA', 'NUMBER', 'COMMA', 'NUMBER', 'RIGHT_BRACKET']
        for token, expected_value, expected_type in zip(tokens[:-1], expected_values, expected_types):
            self.assertEqual(token.value, expected_value)
            self.assertEqual(token.type, expected_type)
        self.assertEqual(tokens[-1].type, 'EOF')

    def test_numbers_edge_cases(self):
        inputs = ['0', '-0', '0.0', '-0.0', '1e-10', '-1E+10', '1.0e0', '1234567890', '9.999999e+307']
        for num_str in inputs:
            tokens = lex(num_str)
            self.assertEqual(len(tokens), 2)
            self.assertEqual(tokens[0].type, 'NUMBER')
            self.assertEqual(tokens[0].value, num_str)
            self.assertEqual(tokens[1].type, 'EOF')

    def test_boolean_and_null(self):
        input_string = '{"bool1": true, "bool2": false, "null_value": null}'
        tokens = lex(input_string)
        expected_types = [
            'LEFT_BRACE', 'STRING', 'COLON', 'TRUE', 'COMMA',
            'STRING', 'COLON', 'FALSE', 'COMMA',
            'STRING', 'COLON', 'NULL', 'RIGHT_BRACE', 'EOF'
        ]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_whitespace_handling(self):
        input_string = '''
        {
            "key1" :   "value1"   ,
            "key2":      42,
            "key3"    :[  1 ,    2,   3    ]
        }
        '''
        tokens = lex(input_string)
        expected_types = [
            'LEFT_BRACE', 'STRING', 'COLON', 'STRING', 'COMMA',
            'STRING', 'COLON', 'NUMBER', 'COMMA',
            'STRING', 'COLON', 'LEFT_BRACKET', 'NUMBER', 'COMMA', 'NUMBER', 'COMMA', 'NUMBER', 'RIGHT_BRACKET',
            'RIGHT_BRACE', 'EOF'
        ]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_unterminated_string(self):
        input_string = '"This string is not closed'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character", str(context.exception))

    def test_invalid_characters(self):
        input_string = '{"key": value@}'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character 'v'", str(context.exception))

    def test_incomplete_number(self):
        input_string = '[123e]'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character ']'", str(context.exception))

    def test_large_input_performance(self):
        # Generate a large JSON array
        large_input = '[' + ', '.join(['{"number": %d}' % i for i in range(10000)]) + ']'
        tokens = lex(large_input)
        # Check that the number of tokens is as expected
        expected_token_count = 4 * 10000 + 2  # 4 tokens per object, times 10000 objects, plus the brackets and EOF
        self.assertEqual(len(tokens), expected_token_count)

    def test_complex_json_structure(self):
        input_json = '''
        {
            "menu": {
                "id": "file",
                "value": "File",
                "popup": {
                    "menuitem": [
                        {"value": "New", "onclick": "CreateNewDoc()"},
                        {"value": "Open", "onclick": "OpenDoc()"},
                        {"value": "Save", "onclick": "SaveDoc()"}
                    ]
                }
            }
        }
        '''
        tokens = lex(input_json)
        token_types = [token.type for token in tokens]
        expected_types_sequence = [
            'LEFT_BRACE', 'STRING', 'COLON', 'LEFT_BRACE',
            'STRING', 'COLON', 'STRING', 'COMMA',
            'STRING', 'COLON', 'STRING', 'COMMA',
            'STRING', 'COLON', 'LEFT_BRACE',
            'STRING', 'COLON', 'LEFT_BRACKET',
            'LEFT_BRACE', 'STRING', 'COLON', 'STRING', 'COMMA', 'STRING', 'COLON', 'STRING', 'RIGHT_BRACE', 'COMMA',
            'LEFT_BRACE', 'STRING', 'COLON', 'STRING', 'COMMA', 'STRING', 'COLON', 'STRING', 'RIGHT_BRACE', 'COMMA',
            'LEFT_BRACE', 'STRING', 'COLON', 'STRING', 'COMMA', 'STRING', 'COLON', 'STRING', 'RIGHT_BRACE',
            'RIGHT_BRACKET', 'RIGHT_BRACE',
            'RIGHT_BRACE',
            'RIGHT_BRACE', 'EOF'
        ]
        self.assertEqual(token_types, expected_types_sequence)

    def test_unicode_characters(self):
        input_string = '{"unicode": "\\u00A9 \\u20AC \\uD83D\\uDE00"}'
        tokens = lex(input_string)
        self.assertEqual(tokens[3].type, 'STRING')
        self.assertEqual(tokens[3].value, '"\\u00A9 \\u20AC \\uD83D\\uDE00"')

    def test_mixed_whitespace(self):
        input_string = '{"key" :\t "value",\n "array":[1,2,\r\n3]}'
        tokens = lex(input_string)
        expected_types = [
            'LEFT_BRACE', 'STRING', 'COLON', 'STRING', 'COMMA',
            'STRING', 'COLON', 'LEFT_BRACKET', 'NUMBER', 'COMMA', 'NUMBER', 'COMMA', 'NUMBER', 'RIGHT_BRACKET',
            'RIGHT_BRACE', 'EOF'
        ]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_multiple_documents(self):
        input_string = '{}{}'
        tokens = lex(input_string)
        expected_types = ['LEFT_BRACE', 'RIGHT_BRACE', 'LEFT_BRACE', 'RIGHT_BRACE', 'EOF']
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_invalid_unicode_escape(self):
        input_string = '"\\uZZZZ"'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character 'Z'", str(context.exception))

    def test_control_characters_in_string(self):
        input_string = '"This string contains control characters \x01\x02\x03"'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character", str(context.exception))

    def test_string_with_escape_sequences(self):
        input_string = '"Line1\\nLine2\\tTabbed\\rCarriage Return\\fForm Feed\\bBackspace"'
        tokens = lex(input_string)
        self.assertEqual(tokens[0].type, 'STRING')
        expected_value = '"Line1\\nLine2\\tTabbed\\rCarriage Return\\fForm Feed\\bBackspace"'
        self.assertEqual(tokens[0].value, expected_value)

    def test_number_with_leading_zeros(self):
        input_string = '[0123]'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character '1'", str(context.exception))

    def test_number_with_invalid_exponent(self):
        input_string = '[1e]'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character ']'", str(context.exception))

    def test_unescaped_control_char_in_string(self):
        input_string = '"This is invalid \x1F"'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character", str(context.exception))

    def test_invalid_token(self):
        input_string = '{"key": #invalid}'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character '#'", str(context.exception))

    def test_object_with_duplicate_keys(self):
        # Note: Lexer does not handle semantic errors like duplicate keys; this is for parser tests
        input_string = '{"key": 1, "key": 2}'
        tokens = lex(input_string)
        expected_types = [
            'LEFT_BRACE', 'STRING', 'COLON', 'NUMBER', 'COMMA',
            'STRING', 'COLON', 'NUMBER', 'RIGHT_BRACE', 'EOF'
        ]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_comments_are_not_allowed(self):
        input_string = '{"key": 1} // This is a comment'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character '/'", str(context.exception))

    def test_malformed_true_literal(self):
        input_string = 'tru'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character", str(context.exception))

    def test_malformed_false_literal(self):
        input_string = 'fals'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character", str(context.exception))

    def test_malformed_null_literal(self):
        input_string = 'nul'
        with self.assertRaises(ValueError) as context:
            lex(input_string)
        self.assertIn("Unexpected character", str(context.exception))

    def test_lex_performance(self):
        import time
        large_input = '[' + ', '.join(['1234567890' for _ in range(100000)]) + ']'
        start_time = time.time()
        tokens = lex(large_input)
        end_time = time.time()
        self.assertLess(end_time - start_time, 2.0)  # Ensure lexing takes less than 2 seconds

if __name__ == '__main__':
    unittest.main()
