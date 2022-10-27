from ctypes import util
from logging import exception
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
		p_node.flags = [
			'-E',
			f'-fplugin={shared.pragmatic_plugin_path}',
			f'-D{shared.PRAGMATIC_MACRO}={shared.meta_path}',
			f'--include={shared.pragmatic_path}/include/preamble.hpp'
			]
		p_node.resolve_command()
	return len(parsed_nodes) > 0

def object_node_generator(node: Node):
	obj_nodes = generate_children(node)
	for o_node in obj_nodes:
		o_node.flags = ['-c']
		o_node.resolve_command()
	return len(obj_nodes) > 0

file_handlers = {
	'.cpp': parsed_node_generator,
	'.ii': object_node_generator
}

def load_meta():
	if shared.meta_path.exists():
		with open(shared.meta_path) as meta_file:
			shared.meta = json.load(meta_file)

def handle_meta_includes():
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
			# Find header node and add source node as child
			found = False
			for node in nodes:
				if node.path == include_path:
					node.add_children(source_node)
					found = True
			if not found:
				header_node = Node(include_path)
				header_node.add_children(source_node)

def handle_meta_sources():
	for source in shared.meta['Sources']:
		# Find node with the same path as the source directive's location
		associating_node: Node = None
		for node in nodes:
			if node.path == Path(source['Location']):
				associating_node = node
				break
		if associating_node == None:
			break
		# Add associations for the node
		for path in source['Path']:
			# Find node to associate
			for node in nodes:
				include_path_relative_to_file: Path = associating_node.dir.joinpath(path)
				if node.path == include_path_relative_to_file:
					if node not in associating_node.associated:
						associating_node.associated.append(node)


def get_leaf_nodes(node: Node) -> list[Node]:
	leaf_nodes: list[Node] = []
	
	if len(node.children) == 0: return [node]
	else:
		for child in node.children:
			leaf_nodes.extend(get_leaf_nodes(child))
	return leaf_nodes

def get_all_children(node: Node, initial:bool=True) -> list[Node]:
	children: list[Node] = []

	if not initial: children.append(node)

	for child in node.children:
		children.extend(get_all_children(child, False))
	return children

def get_all_parents(node: Node, initial:bool=True):
	parents: list[Node] = []

	if not initial: parents.append(node)

	for parent in node.parents:
		parents.extend(get_all_parents(parent, False))
	return parents

def get_node_group(path: Path) -> list[Node]:
	node_group: list[Node] = []
	
	# Get initial node
	initial_node: Node = None
	for node in nodes:
		if node.path == path:
			initial_node = node
			break
	if initial_node == None: return node_group

	# Each iteration is a translation unit
	starter_nodes: list[Node] = [initial_node]
	for starter_node in starter_nodes:
		# Find leaves from initial node
		leaves = get_leaf_nodes(starter_node)

		# Get all parents (collect all files needed for translation unit)
		translation_unit_files: list[Node] = []
		for leaf in leaves:
			translation_unit_files.extend(get_all_parents(leaf, False))

		# Add nodes from current translation unit files
		for node in translation_unit_files:
			if node not in node_group: node_group.append(node)

		# Get all header & source files from current group and find associated files
		hpp_cpp_nodes = [hpp_cpp_nodes for hpp_cpp_nodes in translation_unit_files if hpp_cpp_nodes.extension == '.hpp' or hpp_cpp_nodes.extension == '.cpp']
		for node in hpp_cpp_nodes:
			for associated_node in node.associated:
				if associated_node not in starter_nodes:
					starter_nodes.append(associated_node)

	return node_group



def handle_meta_targets():
	for target in shared.meta['Targets']:
		# If no node exists for target, create one
		target_node: Node = None
		for node in nodes:
			if node.filename == target['Name'] and node.extension == '.exe':
				target_node = node
				break
		if target_node is None:
			target_node = Node(shared.initial_path.joinpath(f'{target["Name"]}.exe'))
			target_node.flags = ['-fuse-ld=lld']

		# Get nodes that belong to target
		node_group = get_node_group(Path(target['Location']))
		# Add object nodes from group to target
		obj_nodes = [node for node in node_group if node.extension == '.obj']
		for obj_node in obj_nodes:
			target_node.add_parents(obj_node)

		# Generate command
		target_node.resolve_command()

	return

def handle_meta_build_options():
	# Iterate over build options
	for build_option in shared.meta['BuildOptions']:
		# Get node group for build option path
		node_group = get_node_group(Path(build_option['Location']))
		# Update build options in all nodes in node group
		for node in node_group:
			if 'Standard' in build_option and node.extension in ['.hpp', '.cpp', '.ii', '.obj']:
				node.flags.append(f'std={build_option["Standard"]}')

def iterate_graph():
	reiterate = False

	load_meta()
	if shared.meta is not None:
		handle_meta_includes()
		handle_meta_sources()
		handle_meta_targets()
		handle_meta_build_options()

	# Generate nodes with file handlers
	for node in nodes:
		reiterate = reiterate or file_handlers.get(node.extension, lambda n: None)(node)

	# Run commands
	for node in nodes:
		if node.command != '' and not node.is_valid and node.is_parents_valid and node.extension != '.exe':
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

	# Run link commands
	for node in nodes:
		if node.command != '' and not node.is_valid and node.is_parents_valid and node.extension == '.exe':
			subprocess.run(node.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			node.CalculateHash()

	return

visual_graph_index = 0
def get_next_visual_graph():
	global visual_graph_index

	re_val = visual_graph_history[visual_graph_index]
	visual_graph_index = (visual_graph_index + 1) % len(visual_graph_history)
	return re_val

visual_graph_size = 0
def get_latest_visual_graph():
	global visual_graph_size

	if len(visual_graph_history) > visual_graph_size:
		visual_graph_size = len(visual_graph_history)
		return visual_graph_history[-1]
	else:
		return None

