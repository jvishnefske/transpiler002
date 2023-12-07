"""this file needs to be rewritten with modular ir_nodes."""
import ast

UnparserBase = ast._Unparser

c_reserved = [
    "auto",
    "break",
    "case",
    "char",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "float",
    "for",
    "goto",
    "if",
    "int",
    "long",
    "register",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "typedef",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while",
]
cpp_reserved = [
    "bool",
    "char",
    "virtual",
    "bitand",
    "dynamic_cast",
    "co_await",
    "not",
    "case",
    "catch",
    "mutable",
    "reflexpr",
    "typedef",
    "int",
    "union",
    "volatile",
    "typename",
    "thread_local",
    "wchar_t",
    "goto",
    "atomic_commit",
    "typeid",
    "throw",
    "alignas",
    "or_eq",
    "atomic_noexcept",
    "extern",
    "void",
    "char32_t",
    "co_yield",
    "while",
    "if",
    "register",
    "constinit",
    "concept",
    "consteval",
    "for",
    "char8_t",
    "static_assert",
    "not_eq",
    "default",
    "try",
    "protected",
    "enum",
    "requires",
    "reinterpret_cast",
    "template",
    "or",
    "static",
    "explicit",
    "this",
    "return",
    "short",
    "constexpr",
    "const_cast",
    "struct",
    "operator",
    "atomic_cancel",
    "xor_eq",
    "long",
    "do",
    "else",
    "compl",
    "bitor",
    "co_return",
    "sizeof",
    "double",
    "delete",
    "and_eq",
    "static_cast",
    "decltype",
    "inline",
    "nullptr",
    "auto",
    "using",
    "synchronized",
    "noexcept",
    "export",
    "signed",
    "asm",
    "class",
    "continue",
    "switch",
    "break",
    "true",
    "new",
    "namespace",
    "private",
    "float",
    "public",
    "const",
    "unsigned",
    "alignof",
    "xor",
    "char16_t",
    "and",
    "friend",
    "false",
]


# here is an experimental version which does not work.


class CppSourceDumper(UnparserBase):
    def __init__(self):
        super().__init__()
        self.source_code = ""

    def generate_source_code(self, node):
        self.visit(node)
        return self.source_code

    def visit_CppAssignment(self, node):
        self.write(f"{node.target} = ")
        self.visit(node.value)
        self.write_line(";")

    def visit_CppReturn(self, node):
        self.write("return ")
        if node.value:
            self.visit(node.value)
        self.write_line(";")

    def visit_CppFunctionDeclaration(self, node):
        self.write_line(f"void {node.name}() {{")
        self.indent()
        for arg in node.args:
            self.visit_CppParameter(arg)
        self.dedent()
        self.write_line("}")

    def visit_CppLambda(self, node):
        self.write_line("[")
        self.indent()
        for arg in node.args:
            self.visit_CppParameter(arg)
        self.write_line("] -> ")
        self.visit(node.body)
        self.dedent()
        self.write_line("}")

    def visit_CppFunctionCall(self, node):
        self.write(node.func_name)
        self.write("(")
        if node.args:
            for arg in node.args:
                self.visit(arg)
                if arg != node.args[-1]:
                    self.write(", ")
        self.write(")")

    def visit_CppParameter(self, node):
        self.write(f"{node.type} {node.name}")

# unused
# class CppAstTransformer(ast.NodeTransformer):
#     def __init__(self):
#         self.variable_stack = []  # Stack to track variable scopes
#
#     def visit_Assign(self, node):
#         # Check if the assignment introduces a new variable
#         if isinstance(node.targets[0], ast.Name):
#             # Define the variable in the current scope
#             self.define_variable(node.targets[0].id, None)
#
#         # Visit the assigned value
#         value = self.visit(node.value)
#
#         # Construct the CppAssignment
#         return CppAssignment(target=node.targets[0].id, value=value)
#
#     def visit_FunctionDef(self, node):
#         # Push the function scope onto the stack
#         self.variable_stack.append([])
#
#         # Visit the function's arguments
#         args = self.visit(node.args)
