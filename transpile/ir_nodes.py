import dataclasses
from typing import Any
import ast


def cnode(cls=None):
    def wrap(cls):
        # mutability is used in the visitor methods inside ast NodeTransformer.
        # hashability is also
        cls = dataclasses.dataclass(cls, frozen=False, unsafe_hash=True)
        cls_dict = cls_dict = dict(cls.__dict__)

        cls_dict["_fields"] = [str(f.name) for f in dataclasses.fields(cls)]
        print(f"definition {cls.__name__} ## {cls_dict['_fields']} ## {dataclasses.fields(cls)}")

        cls = type(cls)(cls.__name__, (ast.AST,) + cls.__bases__, cls_dict)
        assert issubclass(cls, ast.AST)
        return cls

    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @cnode without parens.
    return wrap(cls)


@cnode
class CExpression:
    """An abstract base class representing C expressions."""

    pass


@cnode
class CLiteralExpr:
    """An expression representing a literal value,
    such as an integer, string, or character."""

    value: Any


@cnode
class CIdentifierExpr:
    """An expression representing a variable identifier."""

    name: str


@cnode
class CUnaryExpr:
    """An expression representing a unary operation,
    such as negation or logical not."""

    operator: str
    operand: CExpression


@cnode
class CBinaryExpr:
    """An expression representing a binary operation, such as addition,
    subtraction, or comparison."""

    operator: str
    left_operand: CExpression
    right_operand: CExpression


@cnode
class CAssignmentExpr:
    """An expression representing an assignment statement."""

    target: CExpression
    value: CExpression


@cnode
class CFunctionCallExpr:
    """An expression representing a function call."""

    name: str
    arguments: list[CExpression]


@cnode
class CStatement:
    """An abstract base class representing C statements."""

    pass


@cnode
class CBlockStmt:
    """A statement representing a block of statements enclosed in curly braces."""

    statements: list[CStatement]


@cnode
class CIfStmt:
    """A conditional statement with an if-else structure."""

    cond_expr: CExpression
    then_block: CBlockStmt
    else_block: CBlockStmt  # | None


@cnode
class CWhileStmt:
    """A looping statement with a while condition."""

    cond_expr: CExpression
    body_block: CBlockStmt


@cnode
class CForStmt:
    """A looping statement with a for-loop structure."""

    init_stmt: CStatement
    cond_expr: CExpression
    update_expr: CExpression  # | None
    body_block: CBlockStmt


@cnode
class CReturnStmt:
    """A statement to return a value from a function."""

    return_value: CExpression  # | None


@cnode
class CFunctionDef:
    """A definition of a C function."""

    name: str
    return_type: str
    parameters: list[(str, str)]
    body: CBlockStmt


@cnode
class CSimpleAssignmentStmt:
    """A statement representing a simple assignment without type information."""

    target: CIdentifierExpr
    value: CExpression


@cnode
class CDeclarationStmt:
    """A statement representing a variable declaration with type information."""

    data_type: str
    declaration: CSimpleAssignmentStmt
