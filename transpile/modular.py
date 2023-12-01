"""
a new modular transformer architecture which includes common front end stage,
and produces an IR which is applicable for c, and c++ source generation from python
input.
"""
import ast
import contextlib

from transpile.ir_nodes import (
    CSimpleAssignmentStmt,
    CAssignmentExpr,
    CForStmt,
    CDeclarationStmt,
    CLiteralExpr,
    CIdentifierExpr,
    CStatement,
    CFunctionDef,
    CIfStmt,
    CUnaryExpr,
    CWhileStmt,
    CReturnStmt,
    CBlockStmt,
    CBinaryExpr,
    CExpression,
    CFunctionCallExpr,
)


class TransformerBase(ast.NodeTransformer):
    """put helper methods here"""

    def traverse(self, node):
        if isinstance(node, list):
            return [self.traverse(n) for n in node]
        else:
            return self.visit(node)


def modular_cpp_unparsers():
    return [
        VariableScopeTransformer,
        ControlFlowTransformer,
        CCodeTransformer,
        CppUnparser,
    ]


def get_variable_type_annotation(node, variable_name):
    if isinstance(node, ast.Assign):
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == variable_name:
            # Check for type annotation in the assignment statement
            if isinstance(node.value, ast.AnnAssign):
                return node.value.annotation.id

    if isinstance(node, ast.FunctionDef):
        for arg in node.args.args:
            if isinstance(arg, ast.arg) and arg.arg == variable_name:
                # Check for type annotation in function argument
                if arg.annotation is not None:
                    return arg.annotation.id
    return None


class VariableScopeTransformer(TransformerBase):
    def __init__(self, fail_on_type_inference_error=False):
        self.fail_on_type_inference_error = fail_on_type_inference_error
        self.scope_stack = [{}]  # A stack to track variable scopes

    def visit_Assign(self, node):
        target = node.targets[0]
        if isinstance(target, ast.Name):
            target_name = target.id
            variable_type = get_variable_type_annotation(node, target_name)
            if variable_type is None:
                if self.fail_on_type_inference_error:
                    raise Exception(f"Variable '{target_name}' type cannot be inferred")
                else:
                    variable_type = "auto"

            # Insert a CDeclarationStmt if the variable is new in the current scope
            if target_name not in self.scope_stack[-1]:
                declaration_stmt = CDeclarationStmt(
                    data_type=variable_type,
                    declaration=CSimpleAssignmentStmt(
                        target=CIdentifierExpr(name=target_name),
                        value=self.visit(node.value),
                    ),
                )
                #node.value = declaration_stmt

        return declaration_stmt

    def visit_FunctionDef(self, node):
        self.scope_stack.append({})  # Create a new scope for the function body

        for arg in node.args.args:
            if isinstance(arg, ast.arg):
                arg_name = arg.arg
                variable_type = get_variable_type_annotation(node, arg_name)
                if variable_type is None:
                    if self.fail_on_type_inference_error:
                        raise Exception(
                            f"Variable '{arg_name}' type cannot be inferred"
                        )
                    else:
                        variable_type = "auto"

                self.scope_stack[-1][arg_name] = variable_type

        node.body = CBlockStmt(self.traverse(node.body))

        self.scope_stack.pop()  # Pop the function scope from the stack

        return node


class ControlFlowTransformer(TransformerBase):
    def visit_If(self, node):
        # Analyze the condition expression and extract relevant information
        condition_expr = self.visit(node.test)

        # Analyze the 'then' block and 'else' block (if present)
        then_block = self.traverse(node.body)
        else_block = self.visit(node.orelse) if node.orelse else None

        # Construct an IR representation for the 'if' statement
        if_stmt = CIfStmt(
            cond_expr=condition_expr, then_block=then_block, else_block=else_block
        )
        if condition_expr.left == "__name__":
            return None

        # todo we need a way to convert the __name__ if statements.
        return None

    def visit_While(self, node):
        # Analyze the condition expression and extract relevant information
        condition_expr = self.visit(node.test)

        # Analyze the loop body
        body_block = self.visit(node.body)

        # Construct an IR representation for the 'while' loop
        while_stmt = CWhileStmt(cond_expr=condition_expr, body_block=body_block)

        return while_stmt

    def visit_For(self, node):
        # Analyze the target variable and its iterator
        target = node.target
        iterator = self.visit(node.iter)

        # Analyze the loop body
        body_block = self.visit(node.body)

        # Construct an IR representation for the 'for' loop
        for_stmt = CForStmt(
            init_stmt=None, cond_expr=None, update_expr=None, body_block=body_block
        )

        return for_stmt


class CCodeTransformer(TransformerBase):
    def __init__(self):
        super().__init__()
        self.disable_semicolons = False

    def visit_Assign(self, node):
        target = node.targets[0]
        if isinstance(target, ast.Name):
            target_name = target.id
            value = self.visit(node.value)

            if self.disable_semicolons:
                return CSimpleAssignmentStmt(
                    target=CIdentifierExpr(name=target_name), value=value
                )
            else:
                assign_stmt = CSimpleAssignmentStmt(
                    target=CIdentifierExpr(name=target_name), value=value
                )
                assign_stmt.semicolon = True
                return assign_stmt

        return node

    def visit_BinOp(self, node):
        operator = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
        }[type(node.op)]

        left_operand = self.visit(node.left)
        right_operand = self.visit(node.right)

        return CBinaryExpr(
            operator=operator, left_operand=left_operand, right_operand=right_operand
        )

    def visit_Num(self, node):
        return CLiteralExpr(value=node.n)

    def visit_Name(self, node):
        return CIdentifierExpr(name=node.id)

    def visit_If(self, node):
        cond_expr = self.visit(node.test)
        then_block = self.visit(node.body)
        else_block = self.visit(node.orelse) if node.orelse else None

        if_stmt = CIfStmt(
            cond_expr=cond_expr, then_block=then_block, else_block=else_block
        )
        if_stmt.semicolon = True
        return if_stmt

    def visit_While(self, node):
        cond_expr = self.visit(node.test)
        body_block = self.visit(node.body)

        while_stmt = CWhileStmt(cond_expr=cond_expr, body_block=body_block)
        while_stmt.semicolon = True
        return while_stmt

    def visit_Return(self, node):
        if node.value:
            return_expr = CReturnStmt(return_value=self.visit(node.value))
        else:
            return_expr = CReturnStmt(return_value=None)

        if self.disable_semicolons:
            return return_expr
        else:
            return_expr.semicolon = True
            return return_expr

    def visit_FunctionDef(self, node):
        function_name = node.name
        # TODO: Implement return type analysis
        return_type = None
        parameters = []

        for arg in node.args.args:
            arg_name = arg.arg
            arg_type = None  # TODO: Implement parameter type analysis
            parameters.append((arg_name, arg_type))

        body_block = self.visit(node.body)

        function_def = CFunctionDef(
            name=function_name,
            return_type=return_type,
            parameters=parameters,
            body=body_block,
        )
        return function_def


UnparserPython = ast._Unparser


class UnparserBase(UnparserPython):
    def __init__(self):
        super().__init__()

        # Initialize indentation counter
        self._indent = 0

    @contextlib.contextmanager
    def cblock(self):
        self.fill("{")
        """Context manager for printing a code block with proper indentation."""
        self._indent += 1
        try:
            yield
        finally:
            self._indent -= 1
            self.fill("}")

    @contextlib.contextmanager
    def cstatement(self):
        """Context manager for printing a statement ending with a semicolon."""
        yield
        self.write(";")
        self.fill()


class CUnparser(UnparserBase):
    """
    This currently makes no attempt at producing, or enforcing MISRA compliant code.
    """

    def __init__(self):
        super().__init__()

    def visit_CLiteralExpr(self, expr: CLiteralExpr):
        self.write(str(expr.value))

    def visit_CIdentifierExpr(self, expr: CIdentifierExpr):
        self.write(expr.name)

    def visit_CSimpleAssignmentStmt(self, stmt: CSimpleAssignmentStmt):
        with self.cstatement():
            self.write(f"{stmt.target.name} = ")
            self.traverse(stmt.value)

    def visit_CDeclarationStmt(self, stmt: CDeclarationStmt):
        with self.cstatement():
            self.write(f"{stmt.data_type} {stmt.declaration.target.name} = ")
            self.traverse(stmt.declaration.value)

    def visit_CBinaryExpr(self, expr: CBinaryExpr):
        self.write("(")
        self.traverse(expr.left_operand)
        self.write(f" {expr.operator} ")
        self.traverse(expr.right_operand)
        self.write(")")

    def visit_CIfStmt(self, stmt: CIfStmt):
        with self.cblock():
            self.write(f"if (")
            self.traverse(stmt.cond_expr)
            self.write("){")
            self.traverse(stmt.then_block)
            self.write("}")

            if stmt.else_block:
                self.write("else")
                self.write("{")
                self.traverse(stmt.else_block)
                self.write("}")

    def visit_CWhileStmt(self, stmt: CWhileStmt):
        with self.cblock():
            self.write(f"while (")
            self.traverse(stmt.cond_expr)
            self.write("){")
            self.traverse(stmt.body_block)
            self.write("}")

    def visit_CReturnStmt(self, stmt: CReturnStmt):
        with self.cstatement():
            self.write("return ")
            if stmt.return_value:
                self.traverse(stmt.return_value)
            self.write(";")

    def visit_CFunctionDef(self, func: CFunctionDef):
        self.write(f"/* need to add correct type here. */ int {func.name}(")

        for param in func.parameters:
            self.write(f"{param[0]} {param[1]}, ")

        if func.parameters:
            self.write(")")
        else:
            self.write(f")")

        with self.cblock():
            self.traverse(func.body)


def convert_python_type_to_c_type(python_type_str):
    try:
        # Split the Python type string using the dot (.) delimiter
        components = python_type_str.split(".")

        # Check if the first component is a known Python type
        if components[0] not in PYTHON_TYPE_TO_C_TYPE_MAP:
            raise InvalidTypeConversionError(f"Unknown Python type: {python_type_str}")

        # Construct the C++ type based on the Python type and components
        c_type = PYTHON_TYPE_TO_C_TYPE_MAP[components[0]]

        # Handle nested types (e.g., `array.array`)
        if len(components) > 1:
            c_type += "["
            for component in components[1:]:
                c_type += convert_python_type_to_c_type(component) + ", "
            c_type = c_type[:-2] + "]"

        return c_type
    except KeyError:
        raise InvalidTypeConversionError(f"Unsupported Python type: {python_type_str}")


# Define a dictionary mapping Python types to their corresponding C++ types
PYTHON_TYPE_TO_C_TYPE_MAP = {
    "str": "std::string",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "list": "std::vector",
    "dict": "std::map",
}


class InvalidTypeConversionError(Exception):
    pass


class CppUnparserBase(CUnparser):
    def __init__(self):
        super().__init__()
        self.type_mapping = {
            "str": "std::string",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list": "std::vector",
            "dict": "std::map",
            "auto": "auto"
        }

    def generic_visit(self):
        # allowing the NodeVisitor. generic_visit would likely clear out all source code,
        # This generally indicates there is a function missing.
        raise RuntimeError(
            "this is not correctly handled by the NodeVisitor, and something is likely wrong here. Maybe one of the visitor functions present in the parse tree are not impelemted correctly.")

    def convert_python_type_to_c_type(self, python_type_str):
        try:
            components = python_type_str.split(".")
            base_type = components[0]
            if base_type not in self.type_mapping:
                raise InvalidTypeConversionError(
                    f"Unknown Python type: {python_type_str}"
                )

            c_type = self.type_mapping[base_type]
            if len(components) > 1:
                c_type += "["
                for component in components[1:]:
                    c_type += self.convert_python_type_to_c_type(component) + ", "
                c_type = c_type[:-2] + "]"

            return c_type
        except KeyError:
            raise InvalidTypeConversionError(
                f"Unsupported Python type: {python_type_str}"
            )

    def visit_CDeclarationStmt(self, stmt: CDeclarationStmt):
        data_type = self.convert_python_type_to_c_type(stmt.data_type)
        with self.cstatement():
            self.fill(f"{data_type} ")
            self.traverse(stmt.declaration)


    def convert_python_type_to_c_type(self, python_type_str):
        try:
            if not python_type_str:
                return "auto"
            components = python_type_str.split(".")
            base_type = components[0]
            if base_type not in self.type_mapping:
                raise InvalidTypeConversionError(
                    f"Unknown Python type: {python_type_str}"
                )

            c_type = self.type_mapping[base_type]
            if len(components) > 1:
                c_type += "["
                for component in components[1:]:
                    c_type += self.convert_python_type_to_c_type(component) + ", "
                c_type = c_type[:-2] + "]"

            return c_type
        except KeyError:
            raise InvalidTypeConversionError(
                f"Unsupported Python type: {python_type_str}"
            )

    def visit_CSimpleAssignmentStmt(self, stmt: CSimpleAssignmentStmt):
        with self.cstatement():
            self.fill(f"{stmt.target.name} = ")
            self.traverse(stmt.value)

    def visit_CAssignmentExpr(self, expr: CAssignmentExpr):
        self.fill(f"{expr.target.name} {expr.operator} ")
        self.traverse(expr.value)

    def visit_CForStmt(self, stmt: CForStmt):
        with (self.cblock()):
            self.write(f"for (")
            self.traverse(stmt.init_stmt)
            self.traverse(stmt.cond_expr)
            self.traverse(stmt.update_expr)
            with self.cblock():
                self.traverse(stmt.body_block)

    def visit_CLiteralExpr(self, expr: CLiteralExpr):
        self.write(str(expr.value))

    def visit_CIdentifierExpr(self, expr: CIdentifierExpr):
        self.write(expr.name)

    def visit_CStatement(self, stmt: CStatement):
        with self.cstatement():
            self.traverse(stmt)

    def visit_CFunctionDef(self, func: CFunctionDef):
        return_type = (
            self.convert_python_type_to_c_type(func.return_type)
            if func.return_type
            else "int"
        )

        self.fill(f"{return_type} {func.name}(")

        params_string = ", ".join([f"{self.convert_python_type_to_c_type(param[1])} {param[0]}" for param in func.parameters ])
        self.write(params_string)
        if func.parameters:
            self.write(")")
        else:
            self.write(")")

        with self.cblock():
            self.traverse(func.body)

    def visit_CIfStmt(self, stmt: CIfStmt):
        with self.cblock():
            self.fill("if (")
            self.traverse(stmt.cond_expr)
            self.write(")")
            with self.cblock():
                self.traverse(stmt.then_block)

            if stmt.else_block:
                self.write("else")
                with self.cblock():
                    self.traverse(stmt.else_block)

    def visit_CUnaryExpr(self, expr: CUnaryExpr):
        self.write(f"{expr.operator}(")
        self.traverse(expr.operand)
        self.write(")")


class CppUnparser(CppUnparserBase):
    def visit_CBlockStmt(self, stmt: CBlockStmt):
        with self.cblock():
            for sub_stmt in stmt.statements:
                self.traverse(sub_stmt)

    def visit_CBinaryExpr(self, expr: CBinaryExpr):
        self.write("(")
        self.traverse(expr.left_operand)
        self.write(f" {expr.operator} ")
        self.traverse(expr.right_operand)
        self.write(")")

    def visit_CExpression(self, expr: CExpression):
        with self.cstatement():
            self.traverse(expr)

    def visit_CFunctionCallExpr(self, expr: CFunctionCallExpr):
        self.fill(expr.name)
        self.write("(")

        for arg in expr.arguments:
            self.traverse(arg)
            if arg != expr.arguments[-1]:
                self.write(", ")

        self.write(")")
