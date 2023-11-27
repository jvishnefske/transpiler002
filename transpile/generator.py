import ast
import enum
from enum import auto

def read_ast(testfile):
    with open(testfile) as input_file:
        _ = input_file.read()
        return ast.parse(_)


def read_file(filename):
    # Read the Python file contents
    with open('myfile.py', 'r') as f:
        source_code = f.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Print the AST
    print(ast.dump(tree))



class CppUnparser(ast._Unparser):
    pass


class CppVisitor(ast.NodeVisitor):
    result = ""
    indent_count = 0
    indent = "  "

    def prepend_indent(self, count, body):
        return self.indent * count * body

    def visit_Expression(self, body):
        self.result += prepend_indent(self.indent, body)

    def to_string(self, node):
        node.visit()

    def indent_block(self, string):
        lines = string.split('\n')
        lines = [self.indent + i for i in lines]
        return '\n'.join(lines)


class PyToCppVisitor(ast.NodeVisitor):
    result = []

    def visit(self, node):
        tree = super().visit(node)
        if not tree:
            return
        cpp_source_generator = CppUnparser
        assert tree
        _ = cpp_source_generator.visit(tree)
        return _



def to_cpp(tree):
    visitor = PyToCppVisitor()
    return visitor.visit(tree)
