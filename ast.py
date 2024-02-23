import javalang
import json

# Lists to be made
package = []
imports = []
basictypes = []
variables = []
classes = []
operators = []


class ASTNode:
    def __init__(self, node_type, role=None, value=None):
        self.node_type = node_type
        self.role = role
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)


def serialize_node(node, parent=None, visited=None):
    global package, imports, basictypes, variables, classes, operators

    if visited is None:
        visited = set()

    if node in visited:
        return

    visited.add(node)

    if isinstance(node, javalang.ast.Node):
        # Create AST node
        ast_node = ASTNode(node_type=type(node).__name__)

        # Assign role and value
        if isinstance(node, javalang.tree.PackageDeclaration):
            package.append(node.name)
        elif isinstance(node, javalang.tree.Import):
            imports.append(node.path)
        elif isinstance(node, javalang.tree.BasicType):
            basictypes.append(node.name)
        elif isinstance(node, javalang.tree.VariableDeclarator):
            variables.append(node.name)
        elif isinstance(node, javalang.tree.ClassDeclaration):
            classes.append(node.name)
        elif isinstance(node, javalang.tree.BinaryOperation):
            operators.append(node.operator)

        # Add the node to its parent's children
        if parent:
            parent.add_child(ast_node)

        # Convert node to a dictionary including its class name and attributes
        for _, child_node in node.filter(javalang.ast.Node):
            serialize_node(child_node, parent=ast_node, visited=visited)

        return ast_node
    elif isinstance(node, list):
        for item in node:
            serialize_node(item, parent=parent, visited=visited)


def java_file_to_ast(java_file_path):
    with open(java_file_path, 'r') as java_file:
        java_code = java_file.read()

    tree = javalang.parse.parse(java_code)

    root_node = ASTNode(node_type="CompilationUnit")
    serialize_node(tree, parent=root_node)

    return root_node


# Usage example
root_node = java_file_to_ast('HelloWorld.java')

# Print collected information sorted
print("Package:", package)
print("Imports:", imports)
print("Basic Types:", basictypes)
print("Variables:", variables)
print("Classes:", classes)
print("Operators:", operators)
