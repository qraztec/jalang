import javalang
import json

def serialize_node(node):
    if isinstance(node, javalang.ast.Node):
        # Convert node to a dictionary including its class name and attributes
        node_dict = {'node_type': type(node).__name__}
        for attr in node.attrs:
            value = getattr(node, attr)
            if isinstance(value, javalang.ast.Node):
                node_dict[attr] = serialize_node(value)
            elif isinstance(value, list):
                node_dict[attr] = [serialize_node(item) if isinstance(item, javalang.ast.Node) else item for item in value]
            elif isinstance(value, set):
                # Convert sets to lists as JSON does not support sets
                node_dict[attr] = [serialize_node(item) if isinstance(item, javalang.ast.Node) else item for item in sorted(value)]
            else:
                node_dict[attr] = value
        return node_dict
    elif isinstance(node, list):
        return [serialize_node(item) for item in node]
    elif isinstance(node, set):
        # Convert sets to lists for serialization
        return [serialize_node(item) for item in sorted(node)]
    else:
        return node


def java_file_to_ast(java_file_path, output_file_path):
    with open(java_file_path, 'r') as java_file:
        java_code = java_file.read()

    tree = javalang.parse.parse(java_code)

    serialized_tree = serialize_node(tree)

    with open(output_file_path, 'w') as output_file:
        json.dump(serialized_tree, output_file, indent=4)

# Usage example
java_file_to_ast('HelloWorld.java', 'output_ast.txt')

