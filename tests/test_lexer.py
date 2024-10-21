import unittest
from src.lexer import lex, Token, LexerError

class TestLexer(unittest.TestCase):
    def test_empty_input(self):
        tokens = lex('')
        self.assertEqual(tokens, [Token('EOF', '', 1, 1)])

    def test_single_tokens(self):
        input_str = '{}[],:'
        expected_tokens = [
            Token('LEFT_BRACE', '{', 1, 1),
            Token('RIGHT_BRACE', '}', 1, 2),
            Token('LEFT_BRACKET', '[', 1, 3),
            Token('RIGHT_BRACKET', ']', 1, 4),
            Token('COMMA', ',', 1, 5),
            Token('COLON', ':', 1, 6),
            Token('EOF', '', 1, 7)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_whitespace_handling(self):
        input_str = ' \t\n\r { \n\t } '
        expected_tokens = [
            Token('LEFT_BRACE', '{', 2, 2),
            Token('RIGHT_BRACE', '}', 3, 2),
            Token('EOF', '', 4, 1)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_simple_string(self):
        input_str = '"hello"'
        expected_tokens = [
            Token('STRING', 'hello', 1, 1),
            Token('EOF', '', 1, 8)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_escaped_characters_in_string(self):
        input_str = '"Line1\\nLine2\\tTabbed\\\\"'
        expected_tokens = [
            Token('STRING', 'Line1\nLine2\tTabbed\\', 1, 1),
            Token('EOF', '', 1, 23)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_unicode_in_string(self):
        input_str = '"Unicode: \\u263A \\u00A9 \\uFFFF"'
        expected_tokens = [
            Token('STRING', 'Unicode: ☺ © �', 1, 1),
            Token('EOF', '', 1, 25)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_invalid_unicode_escape(self):
        input_str = '"Invalid unicode: \\u12G4"'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Invalid Unicode escape character: G", str(context.exception))

    def test_unterminated_string(self):
        input_str = '"This string never ends...'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Unterminated string literal", str(context.exception))

    def test_invalid_escape_character(self):
        input_str = '"Invalid escape: \\x"'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Invalid escape character: \\x", str(context.exception))

    def test_numbers(self):
        input_str = '-123 0 456.789 -0.123 1e10 -2E-5'
        expected_tokens = [
            Token('NUMBER', '-123', 1, 1),
            Token('NUMBER', '0', 1, 6),
            Token('NUMBER', '456.789', 1, 8),
            Token('NUMBER', '-0.123', 1, 16),
            Token('NUMBER', '1e10', 1, 23),
            Token('NUMBER', '-2E-5', 1, 28),
            Token('EOF', '', 1, 33)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_invalid_number_leading_zero(self):
        input_str = '0123'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Numbers cannot have leading zeros", str(context.exception))

    def test_invalid_number_format(self):
        input_str = '-'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Invalid number format", str(context.exception))

    def test_boolean_literals(self):
        input_str = 'true false'
        expected_tokens = [
            Token('BOOLEAN', 'true', 1, 1),
            Token('BOOLEAN', 'false', 1, 6),
            Token('EOF', '', 1, 11)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_null_literal(self):
        input_str = 'null'
        expected_tokens = [
            Token('NULL', 'null', 1, 1),
            Token('EOF', '', 1, 5)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_mixed_tokens(self):
        input_str = '{"key1": "value1", "key2": 123, "key3": true, "key4": null}'
        expected_tokens = [
            Token('LEFT_BRACE', '{', 1, 1),
            Token('STRING', 'key1', 1, 2),
            Token('COLON', ':', 1, 8),
            Token('STRING', 'value1', 1, 10),
            Token('COMMA', ',', 1, 18),
            Token('STRING', 'key2', 1, 20),
            Token('COLON', ':', 1, 26),
            Token('NUMBER', '123', 1, 28),
            Token('COMMA', ',', 1, 31),
            Token('STRING', 'key3', 1, 33),
            Token('COLON', ':', 1, 39),
            Token('BOOLEAN', 'true', 1, 41),
            Token('COMMA', ',', 1, 45),
            Token('STRING', 'key4', 1, 47),
            Token('COLON', ':', 1, 53),
            Token('NULL', 'null', 1, 55),
            Token('RIGHT_BRACE', '}', 1, 59),
            Token('EOF', '', 1, 60)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_nested_structures(self):
        input_str = '{"array": [1, 2, 3], "object": {"nested_key": "nested_value"}}'
        expected_tokens = [
            Token('LEFT_BRACE', '{', 1, 1),
            Token('STRING', 'array', 1, 2),
            Token('COLON', ':', 1, 9),
            Token('LEFT_BRACKET', '[', 1, 11),
            Token('NUMBER', '1', 1, 12),
            Token('COMMA', ',', 1, 13),
            Token('NUMBER', '2', 1, 15),
            Token('COMMA', ',', 1, 16),
            Token('NUMBER', '3', 1, 18),
            Token('RIGHT_BRACKET', ']', 1, 19),
            Token('COMMA', ',', 1, 20),
            Token('STRING', 'object', 1, 22),
            Token('COLON', ':', 1, 29),
            Token('LEFT_BRACE', '{', 1, 31),
            Token('STRING', 'nested_key', 1, 32),
            Token('COLON', ':', 1, 43),
            Token('STRING', 'nested_value', 1, 45),
            Token('RIGHT_BRACE', '}', 1, 59),
            Token('RIGHT_BRACE', '}', 1, 60),
            Token('EOF', '', 1, 61)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_control_character_in_string(self):
        input_str = '"Invalid\x01Character"'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Invalid control character in string", str(context.exception))

    def test_unexpected_character(self):
        input_str = '@'
        with self.assertRaises(LexerError) as context:
            lex(input_str)
        self.assertIn("Unexpected character: @", str(context.exception))

    def test_line_and_column_tracking(self):
        input_str = '{\n\t"key": "value"\n}'
        expected_tokens = [
            Token('LEFT_BRACE', '{', 1, 1),
            Token('STRING', 'key', 2, 2),
            Token('COLON', ':', 2, 8),
            Token('STRING', 'value', 2, 10),
            Token('RIGHT_BRACE', '}', 3, 1),
            Token('EOF', '', 3, 2)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_large_input_performance(self):
        input_str = '[' + ', '.join(['{"id": %d, "value": "item%d"}' % (i, i) for i in range(1000)]) + ']'
        tokens = lex(input_str)
        # Check first few and last few tokens
        self.assertEqual(tokens[0], Token('LEFT_BRACKET', '[', 1, 1))
        self.assertEqual(tokens[-1], Token('RIGHT_BRACKET', ']', 1, len(input_str)))
        self.assertEqual(len(tokens), 1000 * 7 + 2)  # Each object has 7 tokens, plus brackets

    def test_escape_forward_slash(self):
        input_str = '"Forward Slash: \\/"'
        expected_tokens = [
            Token('STRING', 'Forward Slash: /', 1, 1),
            Token('EOF', '', 1, 20)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_escape_backspace_formfeed(self):
        input_str = '"Backspace:\\b Formfeed:\\f"'
        expected_tokens = [
            Token('STRING', 'Backspace:\x08 Formfeed:\x0c', 1, 1),
            Token('EOF', '', 1, 25)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_escape_carriage_return(self):
        input_str = '"Carriage Return:\\r End"'
        expected_tokens = [
            Token('STRING', 'Carriage Return:\r End', 1, 1),
            Token('EOF', '', 1, 23)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_escape_tab(self):
        input_str = '"Tab\\tCharacter"'
        expected_tokens = [
            Token('STRING', 'Tab\tCharacter', 1, 1),
            Token('EOF', '', 1, 16)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

    def test_multiple_strings(self):
        input_str = '"first" "second" "third"'
        expected_tokens = [
            Token('STRING', 'first', 1, 1),
            Token('STRING', 'second', 1, 8),
            Token('STRING', 'third', 1, 16),
            Token('EOF', '', 1, 23)
        ]
        tokens = lex(input_str)
        self.assertEqual(tokens, expected_tokens)

if __name__ == '__main__':
    unittest.main()
