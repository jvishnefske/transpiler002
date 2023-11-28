import ast
from transpile.details import cpp_reserved, c_reserved


def read_ast(testfile):
    with open(testfile) as input_file:
        _ = input_file.read()
        return ast.parse(_)


def read_file(filename):
    # Read the Python file contents
    with open(filename, "r") as f:
        source_code = f.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Print the AST
    print(ast.dump(tree))


class CppVisitor(ast.NodeVisitor):
    result = ""
    indent_count = 0
    indent = "  "

    def to_string(self, node):
        node.visit()

    def indent_block(self, string):
        lines = string.split("\n")
        lines = [self.indent + i for i in lines]
        return "\n".join(lines)


def to_cpp(tree):
    visitor = PyToCppTransformer()
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


class CppMultiLineComment(ast.AST):
    pass


class PyToCppTransformer(ast.NodeTransformer):
    def visit(self, node):
        self.includes = set()
        return super().visit(node)

    def visit_BinOp(self, node):
        if node.op == "Pow":
            raise NotImplementedError
        if node.op == "FloorDiv":
            raise NotImplementedError

    def check_identifier(self, node):
        if node.id in cpp_reserved:
            raise NotImplementedError
        if node.id in c_reserved:
            raise NotImplementedError


Unparser = ast._Unparser


class CppUnparser(Unparser):
    def visit_CppCodeBlock(self, node):
        self.fill("{")
        self.traverse(node)
        self.write("}")

    def visit_CppLambda(self, node):
        self.write("[](){")
        self.traverse(node.body)
        self.write("};")

    def visit_CppVariableDeclaration(self, node):
        self.write(f"constexpr {self.type}, {self.id};")

    def visit_CppStruct(self, node):
        self.write("struct ")
        self.write(node.id)
        self.write("{")
        self.traverse(self.body)
        self.write("};")

    def visit_CppMultiLineComment(self, node):
        self.write("/* \n")
        self.traverse(self.body)
        self.write("\n*/")
