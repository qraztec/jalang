import javalang
import json

# Lists to be made
#package = []
#imports = []
datatypes = []
operators = []
reserved_words = []
identifiers = []
assignments = []
literals = []


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
        #if isinstance(node, javalang.tree.PackageDeclaration):
      #      package.append(node.name)
      #  elif isinstance(node, javalang.tree.Import):
     #       imports.append(node.path)
        if isinstance(node, javalang.tree.BasicType):
            datatypes.append(node.name)
        elif isinstance(node, javalang.tree.Literal):
            literals.append(node.value)
        elif isinstance(node, javalang.tree.VariableDeclarator) or isinstance(node, javalang.tree.ClassDeclaration) or isinstance(node, javalang.tree.MethodDeclaration) or isinstance(node, javalang.tree.FormalParameter):
            if hasattr(node, 'modifiers'):
                for modifier in node.modifiers:
                    if modifier in {"public", "private", "protected"}:
                        reserved_words.append(modifier)
            identifiers.append(node.name)

            if hasattr(node, 'modifiers'):
                if "static" in node.modifiers:
                    reserved_words.append("static")
            if hasattr(node, 'return_type'):
                if node.return_type is None:
                    reserved_words.append("void")


          #  if isinstance(node.return_type, javalang.tree.BasicType) and node.return_type.name == "void":
           #     reserved_words.append("void")
        elif isinstance(node, javalang.tree.BinaryOperation):
            operators.append(node.operator)
        elif isinstance(node, javalang.tree.Assignment):
            assignments.append(node.type)
            lhs = node.expressionl
            rhs = node.value
            if (isinstance(lhs, javalang.tree.MemberReference)):
                identifiers.append(lhs.member)
            if (isinstance(rhs, javalang.tree.MemberReference)):
                identifiers.append(rhs.member)
        elif isinstance(node, javalang.tree.ReturnStatement):
            reserved_words.append("return")
            expression = node.expression

            if (isinstance(expression, javalang.tree.BinaryOperation)):
                left = expression.operandl
                right = expression.operandr
                if (isinstance(left, javalang.tree.MemberReference)):
                    identifiers.append(left.member)
                if (isinstance(right, javalang.tree.MemberReference)):
                    identifiers.append(right.member)
        elif isinstance(node, javalang.tree.IfStatement):
            reserved_words.append("if")
        #detects modifiers such as public, private, or protected


        #elif isinstance(node, javalang.tree.)

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
#print("Package:", package)
#print("Imports:", imports)
print("Data Types:", datatypes)
print("Operators:", operators)
print("Reserved Words:", reserved_words)
print("Identifiers:", identifiers)
print("Assignments:", assignments)
print("Literals:", literals)
