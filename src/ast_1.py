
import ast
from typing import List, Union

class ASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        self.generic_visit(node)

def parse_ast(code: str) -> Union[ast.AST, List[ast.AST]]:
    return ast.parse(code)

def analyze_ast(tree: Union[ast.AST, List[ast.AST]]) -> dict:
    visitor = ASTVisitor()
    visitor.visit(tree)
    return {
        "imports": visitor.imports,
        "functions": visitor.functions,
        "classes": visitor.classes
    }

def get_ast_info(code: str) -> dict:
    tree = parse_ast(code)
    return analyze_ast(tree)
