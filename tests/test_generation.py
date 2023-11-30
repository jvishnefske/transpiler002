"""attempt to generate files from source input"""
import ast
import logging
from pathlib import Path
import cppyy
from transpile import generator
from transpile.generator import read_ast, to_cpp
from transpile.ir_nodes import (CDeclarationStmt, CIdentifierExpr,
                                CSimpleAssignmentStmt, CLiteralExpr)

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

testfile = Path(__file__).parent / "example/input01.py"


def test_dumpast():
    my_ast = None
    my_ast = read_ast(testfile)
    logger.info(my_ast)
    logger.info(ast.dump(
        my_ast, annotate_fields=True, include_attributes=False, indent="  "))
    logger.info(ast.unparse(my_ast))
    logger.info("ast test complete.")


def test_src_transformation():
    """without helper function"""
    tree = read_ast(testfile)
    _ = tree
    transformer = generator.PyToCppTransformer()
    src_code_generator = generator.CppUnparser()
    print(ast.dump(
        tree, annotate_fields=True, include_attributes=False, indent=" "))
    _ = transformer.visit(_)

    print(f"after transform: \n {ast.dump(_)}")
    src = src_code_generator.visit(_)
    print(src)
    assert cppyy.cppdef(src)


def disabled_test_compile_generated_cpp():
    my_ast = read_ast(testfile)
    cpp_src = to_cpp(my_ast)
    logger.info("starting ast test")
    logger.info(f"{cpp_src}")
    assert isinstance(cpp_src, str)


def test_unparse():
    # example of embedding raw output code into an ast.
    src = """
    #include <iostream>
    int main(){
    std::cout << "hello" <<std::endl;
    }
    """
    my_ast = [
        ast.Name(id=src)
    ]
    result = ast.unparse(my_ast)
    assert result == src


def test_cppyy():
    """compile some random code, and check that
    the binary exists in memory."""
    definition = cppyy.cppdef(
        """
     class MyClass {
     public:
         MyClass(int i) : m_data(i) {}
         virtual ~MyClass() {}
         virtual int add_int(int i) { return m_data + i; }
         int m_data;
     };"""
    )
    assert definition
    assert hasattr(cppyy.gbl, "MyClass")


def test_c_literal_expr():
    """Test the CLiteralExpr node."""
    literal_expr = CLiteralExpr(value=10)
    assert literal_expr.value == 10


def test_cidentifier_expr():
    """Test the CIdentifierExpr node."""
    identifier_expr = CIdentifierExpr(name="x")
    assert identifier_expr.name == "x"


def test_csimple_assignment_stmt():
    """Test the CSimpleAssignmentStmt node."""
    assign_stmt = CSimpleAssignmentStmt(
        target=CIdentifierExpr(name="x"), value=CLiteralExpr(value=5)
    )
    assert assign_stmt.target.name == "x"
    assert assign_stmt.value.value == 5


def test_cdeclaration_stmt():
    """Test the CDeclarationStmt node."""
    declare_stmt = CDeclarationStmt(
        data_type="int",
        declaration=CSimpleAssignmentStmt(
            target=CIdentifierExpr(name="x"), value=CLiteralExpr(value=10)
        ),
    )
    assert declare_stmt.data_type == "int"
    assert declare_stmt.declaration.target.name == "x"
    assert declare_stmt.declaration.value.value == 10
