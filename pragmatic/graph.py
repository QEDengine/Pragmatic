from pathlib import Path
import subprocess
import json
from sys import meta_path

from pyparsing import empty

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
		flags = [
			'-E',
			f'-fplugin={shared.pragmatic_plugin_path}',
			f'-D{shared.PRAGMATIC_MACRO}={shared.meta_path}',
			f'--include={shared.pragmatic_path}/include/preamble.hpp'
			]
		inputs = [str(parent.path) for parent in p_node.parents]
		output_path = f'{p_node.dir}/{p_node.filename}.ii'
		p_node.command = f'{shared.clang_path} {" ".join(flags)} {" ".join(inputs)} -o {output_path}'
	return len(parsed_nodes) > 0

def object_node_generator(node: Node):
	obj_nodes = generate_children(node)
	for o_node in obj_nodes:
		flags = ['-c']
		inputs = [str(parent.path) for parent in o_node.parents]
		output_path = f'{o_node.dir}/{o_node.filename}.obj'
		o_node.command = f'{shared.clang_path} {" ".join(flags)} {" ".join(inputs)} -o {output_path}'
	return len(obj_nodes) > 0

def target_node_generator(node: Node):
	target_nodes = generate_children(node)
	for t_node in target_nodes:
		flags = ['-fuse-ld=lld']
		output_path = f'{shared.initial_path}/{"basic"}.exe'
		paths: list[str] = []
		for node in nodes:
			if node.extension == '.obj':
				paths.append(str(node.path))
				t_node.add_parents(node)
		t_node.command = f'{shared.clang_path} {" ".join(flags)} {" ".join(paths)} -o {output_path}'
	return len(target_nodes) > 0

file_handlers = {
	'.cpp': parsed_node_generator,
	'.ii': object_node_generator,
	'.obj': target_node_generator
}

def iterate_graph():
	reiterate = False

	# Load meta
	if shared.meta_path.exists():
		with open(shared.meta_path) as meta_file:
			shared.meta = json.load(meta_file)
	
	# Handle includes
	for includes_in_file in shared.meta['Includes']:
		source_node = [s_node for s_node in nodes if s_node.path == Path(includes_in_file["Location"])]
		if len(source_node) == 1: source_node = source_node[0]
		else:
			source_node = Node(includes_in_file['Location'])
		for include in includes_in_file['Path']:
			# resolve include path
			# TODO: update this for include diretories
			relative_path = source_node.dir.joinpath(Path(include))
			include_path = relative_path if relative_path.exists() else Path(include)
			if not any(node for node in nodes if node.path == include_path):
				header_node = Node(include_path)
				header_node.add_children(source_node)

	# Generate nodes
	for node in nodes:
		reiterate = reiterate or file_handlers.get(node.extension, lambda n: None)(node)

	# Run commands
	for node in nodes:
		if node.command != '' and not node.is_valid and node.is_parents_valid:
			subprocess.run(node.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			node.CalculateHash()
			reiterate = True

	# Validate
	for node in nodes:
		if node.extension == '.cpp' or node.extension == '.hpp':
			if all(child.is_hash_valid for child in node.children): node.CalculateHash()

	serialize_graph()
	return reiterate

def scan_directory(path: Path):	
	# glob all files
	sources = list(path.glob('**/*.cpp'))
	headers = list(path.glob('**/*.hpp'))

	# create source nodes
	for source in sources:
		source_node = Node(source)
		source_node.CalculateHash()

	while iterate_graph():
		pass
	return

def test(index: int = 0):
	return visual_graph_history[-1]
