import ast
import enum
from enum import auto

c_reserved = ["auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern",
              "float", "for", "goto", "if", "int", "long", "register", "return", "short", "signed", "sizeof", "static",
              "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"]

cpp_reserved = ["bool", "char", "virtual", "bitand", "dynamic_cast", "co_await", "not", "case", "catch", "mutable",
                "reflexpr", "typedef", "int", "union", "volatile", "typename", "thread_local", "wchar_t", "goto",
                "atomic_commit", "typeid", "throw", "alignas", "or_eq", "atomic_noexcept", "extern", "void", "char32_t",
                "co_yield", "while", "if", "register", "constinit", "concept", "consteval", "for", "char8_t",
                "static_assert", "not_eq", "default", "try", "protected", "enum", "requires", "reinterpret_cast",
                "template", "or", "static", "explicit", "this", "return", "short", "constexpr", "const_cast", "struct",
                "operator", "atomic_cancel", "xor_eq", "long", "do", "else", "compl", "bitor", "co_return", "sizeof",
                "double", "delete", "and_eq", "static_cast", "decltype", "inline", "nullptr", "auto", "using",
                "synchronized", "noexcept", "export", "signed", "asm", "class", "continue", "switch", "break", "true",
                "new", "namespace", "private", "float", "public", "const", "unsigned", "alignof", "xor", "char16_t",
                "and", "friend", "false"]

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


class CppRangedFor(ast.AST):
    pass


class spdlog(ast.AST):
    pass


class CppInclude(ast.AST):
    pass


class CppVariableDefinition(ast.AST):
    pass


class CppLambda(ast.AST):
    pass


class CppStruct(ast.AST):
    pass


class CppUnparser(ast._Unparser):

    def visit_CppCodeBlock(self, node):
        self.fill("{")
        self.traverse(node)
        self.write("}")

    def visit_CppLambda(self, node):
        self.write("[](){")
        self.traverse(node.body)
        self.write("};")

    def visit_CppVariableDeclaration(self, node):
        self.write(f"self.type, self.id")

    def visit_CppStruct(self, node):
        self.write("struct ")
        self.write(node.id)
        self.write("{")
        self.traverse(self.body)
        self.write("};")



