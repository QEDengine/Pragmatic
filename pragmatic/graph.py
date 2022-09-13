from pathlib import Path
import subprocess

from .node import Node
from . import shared
from . import utility


nodes: list[Node] = []
visual_graph_history: list = []

extenion_order = {
	'.cpp': '.ii',
	'.ii': '.obj',
	'.obj': '.exe'
}

def serialize_graph():
	serialized = {}
	serialized['nodes'] = []
	for node in nodes:
		serialized['nodes'].append(node.serialize_node())

	serialized['links'] = []
	for node in nodes:
		serialized['links'].extend(node.serialize_links())

	visual_graph_history.append(serialized)

def generate_children(node: Node) -> list[Node]:
	children = []
	if not any(filter(lambda n: n.filename == node.filename and n.extension == extenion_order[node.extension], node.children)):
		child_node = Node(f'{node.dir}/{node.filename}{extenion_order[node.extension]}')
		node.add_children(child_node)
		children.append(child_node)
	return children

def parsed_node_generator(node: Node):
	parsed_nodes = generate_children(node)
	for p_node in parsed_nodes:
		flags = ['-E', f'-D{shared.PRAGMATIC_MACRO}={shared.meta_path}', f'-fplugin={shared.pragmatic_plugin_path}']
		inputs = [str(parent.path) for parent in p_node.parents]
		output_path = f'{p_node.dir}/{p_node.filename}.ii'
		p_node.command = f'{shared.clang_path} {" ".join(flags)} {" ".join(inputs)} -o {output_path}'
	return len(parsed_nodes) > 0

def object_node_generator(node: Node):
	obj_nodes = generate_children(node)
	return len(obj_nodes) > 0

def target_node_generator(node: Node):
	target_node = generate_children(node)
	return len(target_node) > 0

file_handlers = {
	'.cpp': parsed_node_generator,
	'.ii': object_node_generator,
	'.obj': target_node_generator
}

def iterate_graph():
	reiterate = False

	# Generate nodes
	for node in nodes:
		reiterate = reiterate or file_handlers.get(node.extension, lambda n: None)(node)

	# Run commands
	for node in nodes:
		if node.command != '' and not node.is_valid:
			subprocess.run(node.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			node.CalculateHash()
			reiterate = True

	# Validate
	for node in nodes:
		if node.extension == '.cpp':
			if all(child.is_hash_valid for child in node.children): node.CalculateHash()

	serialize_graph()
	return reiterate

def scan_directory(path: Path):	
	# glob all files
	sources = list(path.glob('**/*.cpp'))
	headers = list(path.glob('**/*.hpp'))

	# create source nodes
	for source in sources:
		Node(source)

	while iterate_graph():
		pass
	return

def test(index: int = 0):
	return visual_graph_history[index]
