from autoslot import Slots
from typing import Tuple
from typing_extensions import Self
from enum import Enum
import os
import pathlib
from pathlib import Path
import subprocess
import networkx as nx

# Const variables
pragmatic_package_dir = os.path.dirname(__file__)
data_dir = f'{pragmatic_package_dir}/data'
clang_exe = f'{data_dir}/LLVM/bin/clang.exe'
pragmatic_meta_macro = 'PRAGMATIC_FILE_PATH'
pragmatic_dll = f'{data_dir}/PragmaticPlugin/PragmaticPlugin.dll'
meta_name = 'meta.json'

# Runtime variables
current_meta_path = None
project_name = None

class Node_type(Enum):
	target = 0
	source = 1
	parsed = 2
	object = 3
	binary = 4
	script = 5

	def infer_from_extension(ext: str) -> Self:
		if ext == 'cpp':
			return Node_type.source
		elif ext == 'ii':
			return Node_type.parsed
		elif ext == 'obj':
			return Node_type.object
		elif ext == 'exe':
			return Node_type.binary
		elif ext == 'py':
			return Node_type.script
		return Node_type.target

class Node(Slots):
	def __init__(self, path: str = '', type: Node_type = None):
		if type != Node_type.target:
			self.path: Path = Path(path)
			self.name = self.path.stem
			self.extension = self.path.suffix.split('.')[1]
			self.dir = self.path.parent
			self.full_name = self.path.name
		self.type = type if type is not None else Node_type.infer_from_extension(self.extension)

		self.cmd = ''

	def run(self):
		if self.cmd != '' and not self.path.exists():
			subprocess.run(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class Command_generator:
	def preprocess_command(node: Node) -> Tuple[str, str]:		
		global current_meta_path
		if not current_meta_path:
			current_meta_path = f'{node.dir}/{meta_name}'

		flags = ['-E', f'-D{pragmatic_meta_macro}={current_meta_path}']
		output_path = f'{node.dir}/{node.name}.ii'
		command = f'{clang_exe} {" ".join(flags)} -fplugin={pragmatic_dll} {node.path} -o {output_path}'
		return (command, output_path)
	def build_command(node: Node) -> Tuple[str, str]:
		flags = ['-c']
		output_path = f'{node.dir}/{node.name}.obj'
		command = f'{clang_exe} {" ".join(flags)} {node.path} -o {output_path}'
		return (command, output_path)
	def link_command(nodes: list[Node]) -> Tuple[str, str]:
		global project_name
		flags = ['-fuse-ld=lld']
		output_path = f'{nodes[0].dir}/{project_name}.exe'
		paths: list[str] = []
		for node in nodes:
			paths.append(str(node.path))
		command = f'{clang_exe} {" ".join(flags)} {" ".join(paths)} -o {output_path}'
		return (command, output_path)
	def generate_command(node: Node) -> str:
		generators = {
					Node_type.source: Command_generator.preprocess_command,
					Node_type.parsed: Command_generator.build_command
				}
		return generators.get(node.type, lambda node: (None, None))(node)

class Graph_build:
	def build(path: str):
		global project_name

		graph = nx.DiGraph()

		project_name = Path(path).stem

		# add default target
		target = Node(type=Node_type.target)
		target.full_name = project_name
		graph.add_node(target.full_name, data = target)
		
		# add initial node
		initial_node = Node(path)
		graph.add_node(initial_node.full_name, data = initial_node)
		graph.add_edge(target.full_name, initial_node.full_name)
		
		Graph_build.generate_graph(graph)
		Graph_build.run_graph(graph)

	def generate_graph(graph: nx.Graph):
		# iterate over graph
		iterate_graph: bool = True
		while iterate_graph:
			iterate_graph = False
			leaf_nodes = [[node, node_data] for node, node_data in graph.nodes().data() if graph.in_degree(node) != 0 and graph.out_degree(node) == 0]
			for leaf, leaf_data in leaf_nodes:
				node_data: Node = leaf_data['data']
				command, output_path = Command_generator.generate_command(node_data)
				if command is not None:
					new_child = Node(output_path, Node_type(node_data.type.value + 1))
					new_child.cmd = command
					graph.add_node(new_child.full_name, data=new_child)
					graph.add_edge(leaf, new_child.full_name)
					iterate_graph = True

		# do one more pass for linking step
		leaf_nodes = [[node, node_data] for node, node_data in graph.nodes().data() if graph.in_degree(node) != 0 and graph.out_degree(node) == 0]
		obj_nodes: list[Node] = []
		for _, node_data in leaf_nodes:
			obj_nodes.append(node_data['data'])
		link_cmd, output_path = Command_generator.link_command(obj_nodes)
		if link_cmd is None:
			raise Exception('No link command generated')
		else:
			new_child = Node(output_path, Node_type.binary)
			new_child.cmd = link_cmd
			graph.add_node(new_child.full_name, data=new_child)
		for leaf, _ in leaf_nodes:
			graph.add_edge(leaf, new_child.full_name)


	def run_graph(graph: nx.Graph):
		topological_generations = [sorted(generation) for generation in nx.topological_generations(graph)]
		for generation in topological_generations:
			print(generation)
			for node in generation:
				node_data: Node = nx.get_node_attributes(graph, 'data')[node]
				node_data.run()




def test_graph():
	graph = nx.DiGraph()
	graph.add_edges_from([("root", "a"), ("a", "b"), ("a", "e"), ("b", "c"), ("b", "d"), ("d", "e"), ('b', 'e')])
	
	print(f'nodes : {graph.nodes()}')
	for path in nx.all_simple_paths(graph, 'root', 'e'):
		print(path)

	leaf_nodes = [node for node in graph.nodes() if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
	print(leaf_nodes)
