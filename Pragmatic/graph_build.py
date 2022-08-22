import graphlib
import shutil
from autoslot import Slots
from typing import List, Tuple
from typing_extensions import Self
from enum import Enum
import os
import pathlib
from pathlib import Path
import subprocess
import networkx as nx
import json
from .FileUtils import hash_str, hash_file

# Const variables
pragmatic_package_dir = os.path.dirname(__file__)
data_dir = f'{pragmatic_package_dir}/data'
clang_exe = f'{data_dir}/LLVM/bin/clang.exe'
pragmatic_meta_macro = 'PRAGMATIC_FILE_PATH'
pragmatic_dll = f'{data_dir}/PragmaticPlugin/PragmaticPlugin.dll'
meta_name = 'meta.json'
build_options_hash_str = 'BuildOptionsHash'
build_options_str = 'BuildOptions'

# Runtime variables
current_meta_path = None
project_name = None
meta: json = None

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
			self.path: Path = Path(path).absolute()
			self.name = self.path.stem
			self.extension = self.path.suffix.split('.')[1]
			self.dir = self.path.parent
			self.full_name = self.path.name
		self.type = type if type is not None else Node_type.infer_from_extension(self.extension)

		self.cmd = ''

	def run(self) -> bool:
		if self.cmd != '' and not self.path.exists():
			subprocess.run(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			return True
		return False

class FlagConverter(Slots):
	def Convert(meta_key: str) -> str:
		if meta_key not in meta[build_options_str]:
			return ''

		if meta_key == 'Standard':
			return f'-std={meta[build_options_str]["Standard"]}'

	def ConvertAll() -> List[str]:
		if meta == None:
			return []
		return [FlagConverter.Convert(key) for key in meta[build_options_str]]


class Command_generator:
	def preprocess_command(node: Node) -> Tuple[str, str]:		
		global current_meta_path
		if not current_meta_path:
			current_meta_path = f'{node.dir}/{meta_name}'

		flags = ['-E', f'-D{pragmatic_meta_macro}={current_meta_path}']
		flags.extend(FlagConverter.ConvertAll())
		flags = [i for i in flags if i is not None]

		output_path = f'{node.dir}/{node.name}.ii'
		command = f'{clang_exe} {" ".join(flags)} -fplugin={pragmatic_dll} {node.path} -o {output_path}'
		return (command, output_path)
	def build_command(node: Node) -> Tuple[str, str]:
		flags = ['-c']
		flags.extend(FlagConverter.ConvertAll())
		flags = [i for i in flags if i is not None]

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
		global meta

		regenerate = True
		while regenerate:
			regenerate = False
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
			
			# iterate over graph
			print('-------------------------------')
			iterate = True
			while iterate:
				# iterate graph
				Graph_build.generate_graph(graph)
				iterate = Graph_build.run_graph(graph, filter=Node_type.parsed)
				
				# load meta
				meta_file = open(current_meta_path)
				meta = json.load(meta_file)
				if build_options_hash_str not in meta:
					meta[build_options_hash_str] = hash_str(json.dumps(meta[build_options_str]))
					with open(current_meta_path, 'w') as outfile:
						json.dump(meta, outfile, indent=4)
				else:
					if meta[build_options_hash_str] != hash_str(json.dumps(meta[build_options_str])):
						meta[build_options_hash_str] = hash_str(json.dumps(meta[build_options_str]))
						with open(current_meta_path, 'w') as outfile:
							json.dump(meta, outfile, indent=4)
						Graph_build.clean(graph)
						regenerate = True
						print('full rebuild required')
						break

				# add new source nodes
				for source in meta['Source']:
					source_path: Path = Path(path).parent / Path(source)
					if not source_path.name in graph.nodes():
						source_node = Node(str(source_path), Node_type.source)
						graph.add_node(source_node.full_name, data = source_node)
						graph.add_edge(target.full_name, source_node.full_name)
						iterate = True

			if regenerate:
				continue
		
		# Run build commands over graph
		Graph_build.generate_link_node(graph)
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
					new_node = Node(output_path, Node_type(node_data.type.value + 1))
					new_node.cmd = command
					graph.add_node(new_node.full_name, data=new_node)
					graph.add_edge(leaf, new_node.full_name)
					iterate_graph = True
	
	def generate_link_node(graph: nx.Graph):
		leaf_nodes = [[node, node_data] for node, node_data in graph.nodes().data() if graph.in_degree(node) != 0 and graph.out_degree(node) == 0]
		obj_nodes: list[Node] = []
		for _, node_data in leaf_nodes:
			leaf_node_data: Node = node_data['data']
			if leaf_node_data.type == Node_type.object:
				obj_nodes.append(leaf_node_data)
		link_cmd, output_path = Command_generator.link_command(obj_nodes)
		if link_cmd is None:
			raise Exception('No link command generated')
		else:
			link_node = Node(output_path, Node_type.binary)
			link_node.cmd = link_cmd
			graph.add_node(link_node.full_name, data=link_node)
		for leaf, leaf_data in leaf_nodes:
			if leaf_data['data'].type == Node_type.object:
				graph.add_edge(leaf, link_node.full_name)

	def run_graph(graph: nx.Graph, filter: Node_type = None) -> bool:
		counter = 0
		topological_generations = [sorted(generation) for generation in nx.topological_generations(graph)]
		for generation in topological_generations:
			print(generation)
			for node in generation:
				node_data: Node = nx.get_node_attributes(graph, 'data')[node]
				if filter is None or node_data.type == filter:
					if node_data.run(): counter += 1
		print('-------------------------------')
		return counter > 0

	def clean(graph: nx.DiGraph, delete_meta: bool = False):
		for node, node_data in graph.nodes().data():
			if node_data['data'].cmd != '' and os.path.exists(node_data['data'].path):
				os.remove(node_data['data'].path)
		if delete_meta:
			if os.path.exists(current_meta_path):
				os.remove(current_meta_path)