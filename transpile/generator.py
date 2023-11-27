import ast


def read_file(filename):
    # Read the Python file contents
    with open('myfile.py', 'r') as f:
        source_code = f.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Print the AST
    print(ast.dump(tree))
