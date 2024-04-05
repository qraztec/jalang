import requests
from bs4 import BeautifulSoup
import javalang
import re
import sys
import time


from javalang.tree import FieldDeclaration

JAVA_DOC_BASE_URL = "https://docs.oracle.com/javase/8/docs/api/"
JAVA_FX_URL = "https://docs.oracle.com/javase/8/javafx/api/"

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
class_labels = []
package_descs = []

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
    #print(class_name)
    packages_list = ["java.util", "java.lang", "java.math", "java.io", "java.nio",
                     "java.net", "java.util.concurrent", "javax.swing", "java.awt",
                     "java.sql", "javax.xml", "java.security", "javafx"]
    if class_name.startswith("javafx."):
        #print(class_name)
        url = f"{JAVA_FX_URL}/{class_name.replace('.','/')}.html"
    else:
        url = f"{JAVA_DOC_BASE_URL}/{class_name.replace('.', '/')}.html"

    #print(class_name)
    try:
        response = requests.get(url)
        if response.status_code == 200:

            for pkg in packages_list:
                if class_name.startswith(pkg + ".") and class_name.count('.') > 1:
                    #   print("Worked")
                    return BeautifulSoup(response.text, 'html.parser')

        else:
            print(f"Failed to fetch JavaDoc for {class_name}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return None

def extract_class_description(soup):
    method_anchor = soup.find(lambda tag: tag.name == "div" and tag.get('class') == ['block'])

    if method_anchor:
        #print("success")

        description_text = ''.join(method_anchor.find_all(string=True, recursive=False)).replace("\n","")
        #i = 0
        for p_tag in method_anchor.find_all('p'):
            # Get only the direct text of each p tag, excluding any text within nested tags
            pure_text = ''.join(p_tag.find_all(string=True, recursive=False))
            pure_text = pure_text.replace("\n", "")
            # Concatenate the pure text to the description_text
            description_text += pure_text

        # for child in method_anchor.children:
        #     if child.find('<p>'):
        #         print(child)
            # if child.find('p'):
            #     print("yes")
            #     description_text += child.string
            #i += 1
        # for p_tag in method_anchor.find_all('<p>'):
        #     description_text += p_tag.get_text(strip=True)

        return description_text


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
            return None#"Description not found."


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
                #print(node)
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

            if isinstance(node, javalang.tree.ClassDeclaration):

                for body in node.body:
                    if isinstance(body, javalang.tree.FieldDeclaration) or isinstance(body, javalang.tree.ConstructorDeclaration):
                        #print(body)
                        if hasattr(body, 'modifiers'):
                            for modifier in body.modifiers:
                                if modifier in {"public", "private", "protected", "static", "final"}:
                                    reserved_words.append(modifier)
                        if hasattr(body, 'declarators'):
                            if hasattr(body, 'type'):
                                var_type = body.type.name
                                #print(var_type)
                                for declarator in body.declarators:
                                    if hasattr(declarator, 'name'):
                                        identifiers.append(declarator.name)
                                        second_dict[declarator.name] = var_type



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
            # if isinstance(node, javalang.tree.VariableDeclarator):
            #     if hasattr(node, 'name'):
            #         #print(node.name)
            #         #print(node)
            #         if node.name in first_dict:
            #             print(node.name)

        elif isinstance(node, javalang.tree.TryStatement):
            reserved_words.append("try")
            if node.catches:
                for catch_clause in node.catches:
                    reserved_words.append("catch")
                    # You can also add catch block parameters to identifiers, if needed
                    if catch_clause.parameter:
                        identifiers.append(catch_clause.parameter.name)

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
                #print(qualif)
                #print(second_dict)
                #print(identifiers)
                if qualif in second_dict:
                    first_word = second_dict[qualif]

                    second_word = first_dict[first_word]
                    soup = fetch_java_doc(second_word)
                    if soup:
                    #print(node.member)
                        description = extract_method_description(soup, node.member, second_word)
                        if description:
                            data = description.replace('\n', "")
                            main_part = data.split('.', 1)[0]

                    # text = f"{javadoc_methods.pop()} - {description}"
                            javadoc_methods.pop()
                            javadoc_methods.append(f"{node.member} - {first_word} - {main_part}")
                    #package_descs.append(extract_class_description(soup))

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
def go_On(root):

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


    # print("First Dict: ", first_dict)
    # print("Second Dict: ", second_dict)
    # print("Packages Id: ", packages_id)

    from g4f.client import Client
    from g4f.Provider import You, GptGo, GptForLove, ChatBase, Chatgpt4Online

    client = Client(
        provider=You
        #api_key = "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"
    )
    # messages = [
    #     {"role": "user",
    #      "content": "You are attempting to classify the inputted description(s) into one of the 31 labels based off of the similarity to it."},
    #
    #     {"role": "user",
    #      "content": "There will be one or more classes to classify. Answer them in the format of: Class: Name of the imported class"
    #                                         "Label: given label of this description"}
    # ]


    def classify_class_description(package_nameAlt, label_options):
        messages = []
        # Construct the prompt with the class name and label options

        prompt = f"Does this class description: Classname: {package_nameAlt}\n"
        prompt += " more fit with which of these options: "
        prompt += f"Options: {label_options}\n"
        prompt += f"Do not respond with any description. Respond exactly in the format: Classname: {package_nameAlt} - Label: [only insert label name]\n"
        messages.append({"role": "user", "content": prompt})
            #time.sleep(4)

        # Add prompt to messages


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
        "Application": "APIs designated for applications provide interfaces for integrating with third-party apps or plugins. They enable the extension of functionality in a primary system, often enhancing user experience or system capabilities through specialized features or services.",
        "Application Performance Manager": "These APIs offer tools for monitoring and analyzing the performance of applications. They can track metrics like response time and resource utilization, providing insights for optimizing software efficiency and reliability.",
        "Big Data": "Big Data APIs are built to handle massive volumes of data, facilitating the collection, storage, processing, and analysis of large datasets. They are optimized for high velocity, variety, and volume data management, essential in fields such as analytics and machine learning.",
        "Cloud": "Cloud APIs provide access to services hosted on virtual networks, including storage, processing power, and cloud databases. They allow for scalable solutions, with remote accessibility and often follow a pay-as-you-go pricing model for resources consumed.",
        "Computer Graphics": "APIs in computer graphics handle the rendering and manipulation of visual content on the screen. They include functions for drawing shapes, text, and images, enabling the development of visually rich applications and games.",
        "Data Structure": "Data Structure APIs offer pre-defined models for organizing and storing data. They encapsulate the complexity of data management, offering efficient ways to access, modify, and traverse different forms of data collections (e.g. collections, lists, trees, sets, graphs, tables)",
        "Databases": "Database APIs define interfaces for interacting with database management systems. They enable the execution of queries, updates, and transactions on databases, abstracting the complexities of direct database manipulation.",
        "Software Development and IT": "DevOps APIs bridge the gap between software development and IT operations, providing tools for automation, continuous integration, deployment, and monitoring, thereby enabling agile development practices and efficient service delivery.",
        "Error Handling": "These APIs are designed to manage errors systematically, offering structures to detect, capture, and handle exceptions. They provide mechanisms for logging errors and recovering application state to prevent system crashes.",
        "Event Handling": "Event Handling APIs allow for asynchronous communication within software via events and listeners. They enable a program to respond dynamically to user interactions, system changes, or other triggers.",
        "Geographic Information System": "GIS APIs deal with the manipulation and analysis of geospatial data, enabling applications to represent, navigate, and interact with maps and geographic information.",
        "Input/Output": "Input-Output APIs are responsible for handling data transfer to and from a system, encompassing both reading from and writing to various data streams, files, or communication channels.",
        "Interpreter": " Interpreter APIs pertain to the features that execute code written in high-level programming languages. They dynamically parse and execute code line by line, which is crucial for scripting and rapid application development environments.",
        "Internationalization": "These APIs help make software globally accessible by supporting various languages, cultural norms, and regional settings. They enable developers to create applications that adapt to multiple languages and regions without code changes.",
        "Logic": "Logic APIs provide the building blocks for creating business logic layers in applications. They contain patterns and frameworks for commands, controls, and data processing, facilitating the implementation of complex algorithmic solutions.",
        "Language": "Language APIs encompass functionalities for handling the peculiarities and constructs of programming languages, such as type conversions, string manipulation, and memory management.",
        "Logging": "Logging APIs are essential for creating a record of application processes. They provide a way to track events, debug issues, and maintain an audit trail, often essential for troubleshooting and compliance.",
        "Machine Learning": "Machine Learning APIs facilitate the creation, training, and deployment of machine learning models. They enable applications to leverage data-driven insights and predictive capabilities without the need for in-depth statistical knowledge.",
        "Microservices/Services": "APIs for microservices are designed to support the development and integration of small, independently deployable services. They focus on enabling these services to communicate and collaborate effectively, often over a network.",
        "Multimedia": "Multimedia APIs support the processing and handling of various media formats, including audio, video, and images. They enable applications to create, manipulate, and transmit multimedia content.",
        "Multithread": "Multi-threading APIs provide mechanisms for applications to perform multiple operations concurrently, leveraging CPU cores efficiently to perform tasks in parallel.",
        "Natural Language Processing": "NLP APIs allow applications to understand and manipulate human language text, enabling features like sentiment analysis, language translation, and chatbots.",
        "Network": "Networking APIs are used to establish and manage connections over a network. They enable data exchange, communication protocols, and network security functions.",
        "Operating System": "OS APIs offer functions for interfacing with the underlying operating system, allowing programs to perform tasks like file management, process control, and memory allocation. These APIs abstract the complexities of dealing with different operating systems, providing a unified way to access essential system resources.",
        "Parser": "Parser APIs break down text or data into a structured format that's easier to work with programmatically. They are used in various contexts, such as interpreting code, processing human languages, or understanding data formats.",
        "Search": "Search APIs enable the querying and retrieval of information from databases, search engines, or other data repositories. They are designed to return relevant results based on specified criteria and often include capabilities for indexing and ranking content.",
        "Security": "Security APIs are crucial in safeguarding applications. They offer functionalities for encryption, authentication, and authorization, helping protect against unauthorized access and ensuring data privacy and integrity.",
        "Setup": "APIs involved in setup processes are designed to configure systems or applications, guiding users through the installation, initialization, and updating phases, often ensuring that the right environment is established for software operation.",
        "User Interface": " User Interface APIs are critical in defining how users interact with applications. They provide a set of controls, such as buttons, text fields, and sliders, and manage user inputs, accessibility, and other aspects of the application's presentation layer.",
        "Utility": "Utility APIs provide a collection of helper functions that are commonly used across various types of applications. They offer generalized solutions for routine programming tasks, such as data manipulation, text processing, and mathematical calculations.",
        "Test": "Test APIs facilitate automated testing of software components. They provide frameworks for unit testing, integration testing, system testing, and acceptance testing, aiming to ensure that code changes do not break existing functionalities."
    }
    # Iterate over imported classes and classify each one
    '''
    for package_nameAlt in packages:

        # Classify the class description using G4P
        g4p_response = classify_class_description(package_nameAlt, options)
        # Extract the classification result from the response
        answer = ""

        for chunk in g4p_response:
            if chunk.choices[0].delta.content:
                answer += (chunk.choices[0].delta.content.strip('*') or "")

        answer = answer.replace("#","")
        answer = answer.lstrip().split('\n')[0]
        class_labels.append(answer+ " (AI) ")
        '''
    #     #print(f"{answer}")


    from gensim import corpora, models, similarities
    from gensim.parsing.preprocessing import preprocess_string

    def find_best_matching_label(package_desc, labels_descriptions):
        #print(package_desc)
        #print(labels_descriptions)
        documents = [package_desc] + list(labels_descriptions.values())
        #print(documents)
        texts = [preprocess_string(doc) for doc in documents]

        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]

        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]

        index = similarities.MatrixSimilarity(corpus_tfidf)

        package_vec = dictionary.doc2bow(preprocess_string(package_desc))
        package_tfidf = tfidf[package_vec]

        sims = index[package_tfidf]
        sims = list(enumerate(sims))[1:]  # Skip the package itself

        highest_sim_index, _ = max(sims, key=lambda item: item[1])
        best_matching_label = list(labels_descriptions.keys())[highest_sim_index - 1]

        return best_matching_label
    #package_desc = "A simple text scanner which can parse primitive types and strings using regular expressions. A Scanner breaks its input into tokens using a delimiter pattern, which by default matches whitespace. The resulting tokens may then be converted into values of different types using the various next methods."

    for i in range(len(packages)):
        soup = fetch_java_doc(packages[i])
        if soup:
            #print(packages[i])
            package_desc = extract_class_description(soup)
            package_descs.append(package_desc)
            best_label = find_best_matching_label(package_desc, options)
            #class_labels[i] += f"- Label: {best_label} (Gensim)"

            g4p_response = classify_class_description(packages[i], options)
            # Extract the classification result from the response
            answer = ""

            for chunk in g4p_response:
                if chunk.choices[0].delta.content:
                    answer += (chunk.choices[0].delta.content.strip('*') or "")

            answer = answer.replace("#", "")
            answer = answer.lstrip().split('\n')[0]

            class_labels.append(f"{answer} (AI) - Label: {best_label} (Gensim)")

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
    print("Class Labels:", class_labels)
    #print("first dict:", first_dict)
    #print("second dict:", second_dict)
    #print("Package Description:", package_descs)
def main():
    while (1):
        try:
            userInput = input(
                "\nPlease Enter a java file: HelloWorld.java | AutosaveManager.java \nBindingsHelper.java | DefaultLatexParser.java | FieldFactory.java\nTicTacToe.java | CrossRef.java | DefaultTexParserTest.java\n OR ENTER exit:\n")
            if (userInput == "exit"):
                print("Exiting the program")
                sys.exit()

            root_node = java_file_to_ast(userInput)
            go_On(root_node)
        except Exception as e:
            print("An error ocurred", e)
if __name__ == "__main__":
    main()

#userInput = input("Please Enter a java file: HelloWorld.java | AutosaveManager.java \nBindingsHelper.java | DefaultLatexParser.java | FieldFactory.java\nTicTacToe.java OR ENTER exit:\n")
