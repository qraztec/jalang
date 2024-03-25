import requests
from bs4 import BeautifulSoup
import javalang
import re

JAVA_DOC_BASE_URL = "https://docs.oracle.com/javase/8/docs/api/"

# Lists to be made
packages = []
packages_id = []
datatypes = []
operators = []
reserved_words = []
identifiers = []
assignments = []
literals = []
methods = []
javadocs = []
javadoc_methods = []

# mapping dictionaries
first_dict = dict()
second_dict = dict()


class ASTNode:
    def __init__(self, node_type, role=None, value=None):
        self.node_type = node_type
        self.role = role
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)


# fetch java documentation from internet and check if can request it
def fetch_java_doc(class_name):
    url = f"{JAVA_DOC_BASE_URL}/{class_name.replace('.', '/')}.html"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            #   print("Worked")
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"Failed to fetch JavaDoc for {class_name}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return None


# get method description from specific java doc online
def extract_method_description(soup, method_name, class_name):
    method_anchor = soup.find(lambda tag: tag.name == "h4" and tag.text == f"{method_name}")

    if method_anchor:
        #  print("success")

        common_parent = method_anchor.find_parent().find_parent()
        description = method_anchor.find_next('div', class_="block")
        description_text = ""
        if description:

            for child in description.children:
                if child.name == "<p>":
                    break
                if child.string:
                    description_text += child.string
            return description_text
        else:
            return "Description not found."


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
            ast_node.value = node.name
        elif isinstance(node, javalang.tree.Literal):
            literals.append(node.value)
        elif isinstance(node, javalang.tree.Import):
            import_path = node.path
            packages.append(import_path)
            # print(import_path)
            package_parts = import_path.split(".")
            if len(package_parts) > 1:
                package_name = package_parts[-2]
                package_nameAlt = package_parts[-1]
                javadocs.append(package_nameAlt)
                first_dict[package_nameAlt] = import_path
                packages_id.append(package_name)
                # print(package_name)
        elif isinstance(node, javalang.tree.LocalVariableDeclaration):
            # identifiers.append(node.name)  # adds all identifiers

            var_type = node.type.name
            if var_type in first_dict:
                for declarator in node.declarators:
                    var_name = declarator.name
                    identifiers.append(var_name)

                    # if var_type in first_dict:
                    #  second_dict[var_name] = var_type
                    #  var_type = first_dict[var_type]
                    second_dict[var_name] = var_type
            '''
            if hasattr(node, 'type'):
                #print(node.name)
                var_type = str(node.type)
                if var_type in first_dict:
                    var_type = first_dict[var_type]
                    second_dict[node.name] = var_type.name
            '''
        elif isinstance(node, javalang.tree.VariableDeclarator) or isinstance(node,
                                                                              javalang.tree.ClassDeclaration) or isinstance(
                node, javalang.tree.MethodDeclaration) or isinstance(node, javalang.tree.FormalParameter):
            if hasattr(node, 'modifiers'):
                for modifier in node.modifiers:
                    if modifier in {"public", "private", "protected"}:
                        reserved_words.append(modifier)

            # identifiers.append(node.name) #adds all identifiers

            if hasattr(node, 'modifiers'):
                if "static" in node.modifiers:
                    reserved_words.append("static")
            if hasattr(node, 'return_type'):
                if node.return_type is None:
                    reserved_words.append("void")
        elif isinstance(node, javalang.tree.BinaryOperation):
            operators.append(node.operator)
            ast_node.value = node.operator
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
            # basic variables
            if (isinstance(expression, javalang.tree.BinaryOperation)):
                left = expression.operandl
                right = expression.operandr

                if (isinstance(left, javalang.tree.MemberReference)):
                    identifiers.append(left.member)

                if (isinstance(right, javalang.tree.MemberReference)):
                    identifiers.append(right.member)

        elif isinstance(node, javalang.tree.IfStatement):
            reserved_words.append("if")
        # gets packages

        # gets methods from the packages, or any extraneous attributes from javadocs

        else:
            # Attempt to handle unrecognized node types
            # Example: Attempt to extract 'name' attribute if present
            if hasattr(node, 'name'):

                javadocs.append(node.name)

            elif isinstance(node, javalang.tree.MethodInvocation) and node.qualifier not in identifiers:
                methods.append(node.member)

            elif isinstance(node, javalang.tree.MethodInvocation) and node.qualifier in identifiers:
                # print("qualifier", node.qualifier)
                qualif = node.qualifier
                javadoc_methods.append(node.member)
                # fetches online description
                first_word = second_dict[qualif]

                second_word = first_dict[first_word]
                soup = fetch_java_doc(second_word)
                if soup:
                    description = extract_method_description(soup, node.member, packages[0])
                    data = description.replace('\n', "")
                    main_part = data.split('.', 1)[0]

                    # text = f"{javadoc_methods.pop()} - {description}"
                    javadoc_methods.pop()
                    javadoc_methods.append(f"{node.member} - {first_word} - {main_part}")

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
# print("Javadoc: ", javadocs)
print("Javadoc Methods: ", javadoc_methods)
# print("First Dict: ", first_dict)
# print("Second Dict: ", second_dict)
# print("Packages Id: ", packages_id)

from g4f.client import Client

client = Client()
messages = [
    {"role": "system",
     "content": "You are attempting to classify the inputted description into one of the 31 labels based off of the similarity to it."},

    {"role": "system",
     "content": "Answer in the format of: Class: Name of the imported class"
                                        "Label: given label of this description"}
]


def classify_class_description(class_name, label_options):
    # Construct the prompt with the class name and label options
    prompt = f"Does this class description: Classname: {class_name}\n"
    prompt += " more fit with which of these options: "
    prompt += f"Options: {label_options}\n"

    # Add prompt to messages
    messages.append({"role": "user", "content": prompt})

    # Send the prompt to G4P for classification
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    return response

# Javax.sql description
description = "Provides the API for server side data source access and processing from the JavaTM programming language."
# Labels and their descriptions
options = {
    "Application": "third party apps or plugins for specific use attached to the system",
    "Application Performance Manager": "monitors performance or benchmark",
    "Big Data": "API's that deal with storing large amounts of data. with variety of formats",
    "Cloud": "APUs for software and services that run on the Internet",
    "Computer Graphics": "Manipulating visual content",
    "Data Structure": "Data structures patterns (e.g., collections, lists, trees)",
    "Databases": "Databases or metadata",
    "Software Development and IT": "Libraries for version control, continuous integration and continuous delivery",
    "Error Handling": "response and recovery procedures from error conditions",
    "Event Handling": "answers to event like listeners",
    "Geographic Information System": "Geographically referenced information",
    "Input/Output": "read, write data",
    "Interpreter": "compiler or interpreter features",
    "Internationalization": "integrate and infuse international, intercultural, and global dimensions",
    "Logic": "frameworks, patterns like commands, controls, or architecture-oriented classes",
    "Language": "internal language features and conversions",
    "Logging": "log registry for the app",
    "Machine Learning": "ML support like build a model based on training data",
    "Microservices/Services": "Independently deployable smaller services. Interface between two different applications so that they can communicate with each other",
    "Multimedia": "Representation of information with text, audio, video",
    "Multithread": "Support for concurrent execution",
    "Natural Language Processing": "Process and analyze natural language data",
    "Network": "Web protocols, sockets RMI APIs",
    "Operating System": "APIs to access and manage a computer's resources",
    "Parser": "Breaks down data into recognized pieces for further analysis",
    "Search": "API for web searching",
    "Security": "Crypto and secure protocols",
    "Setup": "Internal app configurations",
    "User Interface": "Defines forms, screens, visual controls",
    "Utility": "third party libraries for general use",
    "Test": "test automation"
}
# Iterate over imported classes and classify each one
for package_nameAlt in packages:
    # Classify the class description using G4P
    g4p_response = classify_class_description(package_nameAlt, options)
    # Extract the classification result from the response
    answer = ""
    for chunk in g4p_response:
        if chunk.choices[0].delta.content:
            answer += (chunk.choices[0].delta.content.strip('*') or "")
    # Print the classification result
    print(f"Classname: {package_nameAlt}, Label: {answer}")