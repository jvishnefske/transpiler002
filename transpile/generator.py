import ast
from transpile.details import cpp_reserved, c_reserved
from contextlib import contextmanager
from transpile.ir_nodes import CSimpleAssignmentStmt

Unparser = ast._Unparser


def transformer_list():
    return [PyToCppTransformer, CppUnparser]


def read_ast(testfile):
    with open(testfile) as input_file:
        _ = input_file.read()
        return ast.parse(_)


def to_cpp(tree):
    _ = tree
    transformer = PyToCppTransformer()
    src_code_generator = CppUnparser()
    _ = transformer.visit(_)
    src = src_code_generator.visit(_)
    return src


class CppRangedFor(ast.AST):
    pass


class CppVariableDefinition(ast.AST):
    pass


class CppLambda(ast.AST):
    _fields = ["id"]


class CppStruct(ast.AST):
    _fields = ["name"]


class CppMultiLineComment(ast.AST):
    _fields = ["value"]


class CppInclude(ast.AST):
    _fields = ["value"]


class CppCodeBlock(ast.AST):
    _fields = ["body"]


class CppFunctionDef(ast.AST):
    _fields = ["name", "args", "returns", "body"]


class CppStatement(ast.AST):
    """a statement ending in a semicolon"""

    _fields = ["body"]


class CppDefinition(ast.AST):
    """a statement ending in a semicolon"""

    _fields = ["body"]


class PyToCppTransformer(ast.NodeTransformer):
    def visit(self, node):
        self.includes = set()
        return super().visit(node)

    def visit_BinOp(self, node):
        if node.op == "Pow":
            raise NotImplementedError
        if node.op == "FloorDiv":
            raise NotImplementedError
        return node

    def check_identifier(self, node):
        if node.id in cpp_reserved:
            raise NotImplementedError
        if node.id in c_reserved:
            raise NotImplementedError

    def visit_Import(self, node):
        # consider using inspect.getsource for module, and generating c++
        # tree. for external module.
        # value=node.names[0].id
        # return ast.Name(f'#include "bits/stdc++.h"')
        result = CppInclude(value="bits/stdc++.h")
        return result

    def traverse(self, node):
        if isinstance(node, list):
            return [self.traverse(i) for i in node]
        else:
            return self.visit(node)

    def visit_FunctionDef(self, node):
        f = CppFunctionDef()
        f.name = node.name
        f.body = CppCodeBlock(body=self.traverse(node.body))
        f.args = node.args
        f.returns = node.returns
        helper = CppUnparser()
        a = node.args
        if a.posonlyargs or a.kw_defaults or a.kwonlyargs or a.defaults:
            raise NotImplementedError
        if docstring := helper.get_raw_docstring(node):
            comment = CppMultiLineComment(value=docstring)
            return [comment, f]
        return f

    def visit_Return(self, node):
        return CppStatement(body=node)

    def visit_Pow(self, node):
        return CppMultiLineComment(value="TODO std::exp(...)")

    def visit_If(self, node):
        return CppMultiLineComment(value="TODO if")

    def visit_Expr(self, node):
        return CppMultiLineComment(value="TODO expression")

    def visit_Assign(self, node):
        return CppDefinition(body=node)


class CppContextTransformer(ast.NodeTransformer):
    """
    Attempt to transform python assignments, and
    create sane cpp definitions considering odr.
    """

    # Class variable to store the nested context stack
    nested_context = []

    def visit_Assign(self, node):
        # Check if the assignment is inside a class or function definition
        nested_context = None
        for parent in node.get_parent():
            if isinstance(parent, ast.ClassDef) or isinstance(parent, ast.FunctionDef):
                nested_context = parent
                break

        # If a nested context exists, push the current
        # variable name and type onto the stack
        if nested_context:
            self.nested_context.append((node.targets[0].id, node.targets[0].type))

        # Visit the assigned value
        value = self.visit(node.value)

        # If a nested context exists, pop the last entry from the stack
        if nested_context:
            self.nested_context.pop()

        # Construct the CppAssign or insert CppDefinition based on the nested context
        if nested_context:
            nested_context.cpp_block.insert_child(
                CppDefinition(target=node.targets[0].id, value=value)
            )
            return None
        else:
            return CSimpleAssignmentStmt(target=node.targets[0].id, value=value)


class CppUnparser(Unparser):
    def visit_CppCodeBlock(self, node):
        with self.cppblock():
            self.traverse(node.body)

    def visit_CppDefinition(self, node):
        self.write("const auto ")
        self.traverse(node.body)
        self.write(";\n")

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
        self.write(node.value)
        self.write("\n*/\n")

    def visit_CppInclude(self, node):
        self.write(f'#include "{node.value}"\n')

    def visit_CppCode(self, node):
        self.write(f"{node.value}")

    def arg_helper(self, node):
        if node:
            self.traverse(node)
            return ""
        # if len(node) > 0:
        #     return ",".join([f"{a.annotation.attr} {a.arg}" for a in node])
        else:
            return "/*empty*/"

    def visit_CppFunctionDef(self, node):
        self.write(f"auto {node.name}(")
        self.traverse(node.args)
        self.write(") ")
        if node.returns:
            self.write("-> ")
            # self.write(f'{node.returns.attr}')
            self.traverse(node.returns)
        # self.write('{\n')
        self.traverse(node.body)
        # self.write('}\n');

    def visit_CppStatement(self, node):
        self.traverse(node.body)
        self.write(";\n")

    def visit_arguments(self, node):
        if node:
            self.write(
                ", ".join([f"{arg.annotation.id} {arg.arg}" for arg in node.args])
            )

    @contextmanager
    def cppblock(self, *, extra=None):
        """A context manager for preparing the source for blocks. It adds
        the character'{', increases the indentation on enter and decreases
        the indentation on exit. If *extra* is given, it will be directly
        appended after the character.
        """
        self.write("{")
        if extra:
            self.write(extra)
        self._indent += 1
        yield
        self._indent -= 1
        self.write("}")
        self.write(node.value)
        self.write("\n*/\n")

    def visit_CppInclude(self, node):
        self.write(f'#include "{node.value}"\n')

    def visit_CppCode(self, node):
        self.write(f'{node.value}')

    def arg_helper(self, node):
        if node:
            self.traverse(node)
            return ""
        # if len(node) > 0:
        #     return ",".join([f"{a.annotation.attr} {a.arg}" for a in node])
        else:
            return "/*empty*/"

    def visit_CppFunctionDef(self, node):
        self.write(f'auto {node.name}(')
        self.traverse(node.args)
        self.write(') ')
        if node.returns:
            self.write('-> ')
            # self.write(f'{node.returns.attr}')
            self.traverse(node.returns)
        # self.write('{\n')
        self.traverse(node.body)
        # self.write('}\n');

    def visit_CppStatement(self, node):
        self.traverse(node.body)
        self.write(';\n')

    def visit_arguments(self, node):
        if node:
            self.write(', '.join(
                [f'{arg.annotation.id} {arg.arg}' for arg in node.args]))

    @contextmanager
    def cppblock(self, *, extra=None):
        """A context manager for preparing the source for blocks. It adds
        the character':', increases the indentation on enter and decreases
        the indentation on exit. If *extra* is given, it will be directly
        appended after the colon character.
        """
        self.write("{")
        if extra:
            self.write(extra)
        self._indent += 1
        yield
        self._indent -= 1
        self.write("}")
