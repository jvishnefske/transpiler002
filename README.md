Embedded Transpiler
==

This module currently only takes very trivial python files and outputs c++.
There is a main function, but it is not yet tested.

<!-- TOC -->
* [Embedded Transpiler](#embedded-transpiler)
  * [Unit tests](#unit-tests)
  * [Stages](#stages)
    * [Stage 1: Analysis](#stage-1-analysis)
    * [Stage 2: Intermediate Representation (IR)](#stage-2-intermediate-representation-ir)
    * [Stage 3: Target Code Generation](#stage-3-target-code-generation)
  * [Intermediate Representation](#intermediate-representation)
  * [Future Consideration](#future-consideration)
<!-- TOC -->

Unit tests
--
    
    poetry install
    poetry run pytest

Stages
---

To maintain consistency between modular transpilers (ie c/c++), a common stage numbering scheme can be used:

### Stage 1: Analysis

1.1: AST Parsing

1.2: Variable Scope Analysis
   - Track variable scopes: Use a stack to track the current scope and nested scopes.
   - Identify global and nonlocal declarations: Handle global and nonlocal keywords to identify global and nonlocal variables.
   - Insert CppDefinitions: Insert CppDefinition nodes for global and nonlocal variables into the appropriate scopes.

1.3: Type Resolution
   - Infer data types from assignments: Infer data types of variables from assignment expressions.
   - Propagate data types through expressions: Propagate data types through expressions to consistent type checking.
   - Handle type annotations: Consider type annotations provided in function arguments and return types.

### Stage 2: Intermediate Representation (IR)

2.1: IR Construction
   - Convert Python statements to Cpp statements: Transform Python statements like Assign, Return, FunctionDef, and Lambda into corresponding Cpp AST nodes.
   - Handle function arguments and return types: Convert Python function arguments and return types into Cpp AST nodes.
   - Generate Cpp expressions from Python expressions: Recursively transform Python expressions into Cpp expressions.
2.2: IR Optimization (Optional)

### Stage 3: Target Code Generation

3.1: Target-Specific Code Generation
   - Generate C/C++ code from Cpp AST: Traverse the Cpp AST and generate corresponding Cpp code.
   - Handle variable declarations and definitions: Insert variable declarations and definitions based on the variable scope analysis.
   - Ensure proper indentation and formatting: Format the generated Cpp code for readability and maintainability.
3.2: Code Formatting

Pluggable Output Stages

To accommodate different target environments or output formats, pluggable output stages can be introduced. These stages can be customized to generate code for specific platforms, integrate with build systems, or produce different code representations.

For instance, if someone wants to make a MISRA C transpiler this may have a pluggable output stage which generates MISRA C code compatible with different compilers or code analyzers. Similarly, the C++ transpiler can have an output stage that generates C++ code for various operating systems or target architectures.


Intermediate Representation
---

The initial implementation uses a tree structure for intermediate representation of analyzed python.

| IR Representation        | Pros                                                             | Cons                                                    |
|--------------------------|------------------------------------------------------------------|---------------------------------------------------------|
| Syntax Tree              | Simple, expressive, adaptable, tool-compatible                   | Can be verbose for complex code                         |
| Three-Address Code       | Compact, efficient                                               | Less expressive, requires more complex transformations  | 
| Control Flow Graph (CFG) | Clear representation of control flow, suitable for optimization  | Less expressive, requires more complex transformations  |



Future Consideration
--

There are a few modifications that can be made to the transformers to enhance project interaction and improve the overall transformation process:

   - Shared Variable Scope Tree: Introduce a shared variable scope tree that is accessible to all transformers. This will ensure that all transformers have consistent access to the variable scope information, minimizing discrepancies and improving consistency.
   - Type Inference Integration: Integrate the data type inference logic into the variable scope tree. This will allow the type inference transformer to update the type annotations directly within the variable scope tree, enabling subsequent transformers to access the updated types seamlessly.
   - Early Type Checks: Implement early type checks during the transformation process. This will help catch potential type errors early on and prevent them from propagating through the transformation stages, reducing the risk of undetected errors.
   - Intermediate Code Representation: Consider introducing an intermediate code representation (ICR) between the AST and the C++ AST. This ICR can serve as a common abstraction for the transformers to operate on, facilitating more efficient and consistent transformations.
   - Modular Transformer Design: Design each transformer as a modular unit with well-defined responsibilities. This will make it easier to understand, maintain, and extend the transformation pipeline, allowing for cleaner separation of concerns.

By implementing these modifications, the transformers can work together more effectively, resulting in a more robust and reliable transformation process.