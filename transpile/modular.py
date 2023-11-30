"""
a new modular transformer archatecture which includes common front end stage,
and produces an IR which is applicable for c, and c++ source generation from python
input.
"""


# A simple decorator which allows new ast.AST I want to define new nodes like this.
# @CNode
# class CFunctionDef:
#     name: str
#     arguments: cargs
#     comment: Optional(str)
#     ...
# The _field list[str] should be generated
