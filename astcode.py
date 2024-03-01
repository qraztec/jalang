import requests
from bs4 import BeautifulSoup
import javalang
import re

JAVA_DOC_BASE_URL = "https://docs.oracle.com/javase/8/docs/api/"


# Lists to be made
packages = []
datatypes = []
operators = []
reserved_words = []
identifiers = []
assignments = []
literals = []
methods = []
javadocs = []
javadoc_methods = []


class ASTNode:
    def __init__(self, node_type, role=None, value=None):
        self.node_type = node_type
        self.role = role
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)


def serialize_node(node, parent=None, visited=None):
    global operators, reserved_words, identifiers, assignments, literals

    if visited is None:
        visited = set()

    if node in visited:
        return

    visited.add(node)

    if isinstance(node, javalang.ast.Node):
        ast_node = ASTNode(node_type=type(node).__name__)

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
        elif isinstance(node, javalang.tree.Import):
            import_path = node.path
            packages.append(import_path)

        else:
            # Attempt to handle unrecognized node types
            # Example: Attempt to extract 'name' attribute if present
            if hasattr(node, 'name'):

                javadocs.append(node.name)

            elif isinstance(node, javalang.tree.MethodInvocation) and node.qualifier not in identifiers:
                methods.append(node.member)
            elif isinstance(node, javalang.tree.MethodInvocation) and node.qualifier in identifiers:
                javadoc_methods.append(node.member)






        if parent:
            parent.add_child(ast_node)

        for _, child_node in node.filter(javalang.ast.Node):
            serialize_node(child_node, parent=ast_node, visited=visited)

        return ast_node
    elif isinstance(node, list):
        for item in node:
            serialize_node(item, parent=parent, visited=visited)


def extract_identifiers_from_comment(comment):
    """
    Extract identifiers from Java documentation comment.
    """
    # Regular expression to match identifier declarations
    pattern = r'@(?:param|return)\s+\w+\s+(\w+)'

    matches = re.findall(pattern, comment)
    return matches


def java_file_to_ast(java_file_path):
    with open(java_file_path, 'r') as java_file:
        java_code = java_file.read()

    tree = javalang.parse.parse(java_code)

    root_node = ASTNode(node_type="CompilationUnit")
    serialize_node(tree, parent=root_node)

    return root_node


# Usage example
root_node = java_file_to_ast('HelloWorld.java')

# Extract identifiers from Java documentation comments
doc_comment = """
/**
 * This is a sample method.
 * @param args An array of strings.
 * @return An integer value.
 */
"""
identifiers_from_comment = extract_identifiers_from_comment(doc_comment)

# Add detected identifiers to the identifiers list
identifiers.extend(identifiers_from_comment)

# Print collected information sorted
print("Packages: ", packages)
print("Data Types:", datatypes)
print("Operators:", operators)
print("Reserved Words:", reserved_words)
print("Identifiers:", identifiers)
print("Assignments:", assignments)
print("Literals:", literals)
print("Methods:", methods)
print("Javadoc: ", javadocs)
print("Javadoc Methods: ", javadoc_methods)
