"""attempt to generate files from source input"""
import ast
import logging
from pathlib import Path

import cppyy
import graphlib
from transpile.generator import PyToCppTransformer, read_ast, to_cpp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")


def test_graphlib():
    graph = {"A": "B", "B": {}}


testfile = Path(__file__).parent / "example/input01.py"


def test_dumpast():
    my_ast = None
    input_string = """print("hello world")
    """
    my_ast = read_ast(testfile)
    print(my_ast)
    print(ast.dump(my_ast, annotate_fields=True, include_attributes=False, indent="  "))
    print(ast.unparse(my_ast))
    print("ast test complete.")


def test_visit_ast():
    visitor = PyToCppTransformer()
    my_ast = read_ast(testfile)
    cpp_src = to_cpp(my_ast)
    #cppyy.cppdef(cpp_src)


class Name(ast.AST):
    """node unparses as only the id string"""
    def __init__(self, code: str):
        #print("id type", type(self.id))
        self.id = code

    # def __class__(self):
    #     return Name

class Expr:
    """ unparses as an indented block of text."""
    def __init__(self, lines):
        self._fields = lines

    def __class__(self):
        return ast.Expr


def test_unparse():
    my_ast = [Name('#include <iostream>\nint main()' ',{std::cout << "hello" <<std::endl;}')]
    print(ast.unparse(my_ast))

def test_cppyy():
    """simply to evaluate the usefulness"""
    definition = cppyy.cppdef("""
     class MyClass {
     public:
         MyClass(int i) : m_data(i) {}
         virtual ~MyClass() {}
         virtual int add_int(int i) { return m_data + i; }
         int m_data;
     };""")
    print(cppyy.gbl.MyClass)
    #help(cppyy.gbl.MyClass)
