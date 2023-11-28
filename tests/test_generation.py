"""attempt to generate files from source input"""
import ast
import logging
from pathlib import Path
import cppyy

from transpile.generator import read_ast, to_cpp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

testfile = Path(__file__).parent / "example/input01.py"


def test_dumpast():
    my_ast = None
    my_ast = read_ast(testfile)
    print(my_ast)
    print(ast.dump(
        my_ast, annotate_fields=True, include_attributes=False, indent="  "))
    print(ast.unparse(my_ast))
    print("ast test complete.")


def test_visit_ast():
    my_ast = read_ast(testfile)
    cpp_src = to_cpp(my_ast)
    cppyy.cppdef(cpp_src)


class Expr:
    """unparses as an indented block of text."""

    def __init__(self, lines):
        self._fields = lines

    def __class__(self):
        return ast.Expr


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
    """simply to evaluate the usefulness"""
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
    cppyy.cppdef(definition)
    assert hasattr(cppyy.gbl, "MyClass")
