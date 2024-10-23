import argparse
import sys
from .lexer import lex
from .parser import Parser
from .ast import ASTNode

def main():
    import json
    arg_parser = argparse.ArgumentParser(description='JSON Parser CLI Tool')
    arg_parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                           help='JSON file to parse (or stdin if not specified)')
    arg_parser.add_argument('--pretty', action='store_true', help='Pretty print the output')
    args = arg_parser.parse_args()

    try:
        input_text = args.file.read()
        tokens = lex(input_text)
        parser = Parser(tokens)
        ast = parser.parse()
        result = ast.evaluate()
        
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
