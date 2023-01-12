from pathlib import Path
import subprocess
import json

from typeguard import typechecked
import networkx as nx

from . import shared
from . import utility

import re

def load_meta() -> bool:
	if shared.meta_path.exists():
		with open(shared.meta_path, 'r', encoding='utf-8') as meta_file:
			shared.meta = json.load(meta_file)
		return True
	else: return False

def save_meta():
	with open(shared.meta_path, 'w') as meta_file:
		json.dump(shared.meta, meta_file, indent=4)#, sort_keys=True)

def resolve_meta_paths(meta_path: str) -> Path:
	return shared.initial_path_dir.joinpath(meta_path)

@typechecked
def run_subprocess(command: str, cwd: Path) -> int:
	# invoke process
	process = subprocess.Popen(command, cwd=cwd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Poll process.stdout to show stdout live
	while True:
		output = process.stdout.readline()
		if process.poll() is not None:
			break
		if output:
			print(output.decode())
	return process.poll()

@typechecked
def compile_source_file(path: Path, metadata: object = None) -> bool:
	rel_path = shared.initial_path_dir.joinpath(path).relative_to(shared.initial_path_dir)
	command = ' '.join([
		f'{shared.clang_path} -c {rel_path} -o {rel_path.with_suffix(".o")}',	# Clang_path -c source.cpp -o source.o
		f'-fplugin={shared.pragmatic_plugin_path}',								# -fplugin=.../pragmatic/pragmatic_plugin/build/PragmaticPlugin.dll
		f'-DPRAGMATIC_FILE_PATH=\"{shared.meta_path}\"',						# -DPRAGMATIC_FILE_PATH="path/to/meta.json"
		f'--include={shared.pragmatic_preamble_path}',							# --include=.../pragmatic/include/preamble.hpp
	])
	if metadata is not None:
		command += ' ' + ' '.join(interpret_metadata(metadata))

	if path.is_file and path.suffix == '.cpp':
		return_code = run_subprocess(command, shared.initial_path_dir)
		return True if return_code == 0 else False
	else: return False

@typechecked
def link_files(paths: list[Path], out_path: Path) -> bool:
	rel_out_path = shared.initial_path_dir.joinpath(out_path).relative_to(shared.initial_path_dir)
	command = ' '.join([
		f'{shared.clang_path} -o {rel_out_path}'	# Clang_path -c source.cpp -o source.o
	])

	for path in paths:
		command += ' ' + str(path)

	return_code = run_subprocess(command, shared.initial_path_dir)
	return True if return_code == 0 else False

@typechecked
def load_graph() -> nx.DiGraph:
	load_meta()
	data = shared.meta['graph']
	graph = nx.DiGraph()
	for node in data['nodes']:
		graph.add_node(node, metadata=data['nodes'][node]['metadata'])
	for edge in data['edges']:
		graph.add_edge(edge['source'], edge['target'], relation=edge['relation'], metadata=edge['metadata'])
	return graph

@typechecked
def update_hashes(graph: nx.DiGraph) -> bool:
	did_update_meta = False
	for node, attribute in graph.nodes().items():
		# Get absolute path
		node_path = resolve_meta_paths(node)

		# Initialize runtime attribute
		if 'runtime' not in attribute:
			attribute['runtime'] = {}

		# Check file exists
		if node_path.exists():
			attribute['runtime']['file_exists'] = True
			node_file_hash = utility.hash_file(node_path)
		else:
			attribute['runtime']['file_exists'] = False
			continue

		# Initialize metadata attribute
		if 'metadata' not in attribute:
			attribute['metadata'] = {}

		# Update hashes
		if ('hash' not in attribute['metadata'] or node_file_hash != attribute['metadata']['hash']):
			attribute['metadata']['hash'] = node_file_hash
			did_update_meta = True
	return did_update_meta

@typechecked
def get_nodes_by_extension(graph: nx.DiGraph, ext: str) -> list[str]:
	nodes = []
	for node in graph.nodes():
		if node.endswith(ext):
			nodes.append(node)

	return nodes

@typechecked
def get_topological_layers(graph: nx.DiGraph) -> list[list[str]]:
	layers = [sorted(generation) for generation in nx.topological_generations(graph)]
	return layers

@typechecked
def get_nodes_leading_to_node(graph:nx.DiGraph, node: str) -> list[str]:
	paths = list(nx.shortest_paths.shortest_path(graph.reverse(), node).keys())
	return paths

@typechecked
def retrieve_graph_meta(graph: nx.DiGraph) -> None:
	node_metadata_attributes = nx.get_node_attributes(graph, 'metadata')
	for node in shared.meta['graph']['nodes']:
		shared.meta['graph']['nodes'][node]['metadata'] = node_metadata_attributes[node]

@typechecked
def interpret_metadata(metadata: object) -> list[str]:
	def stardard(std: str):
		return f'-std={std}'

	metadata_handlers = {
		'standard': stardard,
	}

	arguments = []
	for key in metadata:
		interpreted_arg = metadata_handlers.get(key, lambda n: None)(metadata[key])
		if interpreted_arg is not None: arguments.append(interpreted_arg)

	return arguments

@typechecked
def run_command(command: str) -> bool:
	return_code = run_subprocess(command, shared.initial_path_dir)
	return True if return_code == 0 else False

@typechecked
def check_edge_input_hashes(graph: nx.DiGraph, edge: object) -> bool:
	node_attributes = nx.get_node_attributes(graph, 'metadata')
	nodes_to_object = get_nodes_leading_to_node(graph, edge[0][1])[1:]
	all_input_hashes_match = True
	if 'input_hashes' not in edge[1]['metadata']:
		all_input_hashes_match = False
	else:
		for i, node in enumerate(nodes_to_object):
			if node_attributes[node]['hash'] != edge[1]['metadata']['input_hashes'][i]:
				all_input_hashes_match = False
				break
	return all_input_hashes_match

@typechecked
def instantiate_command(command_template: str, edge: object) -> str:
	return command_template.format(
							clang_path=shared.clang_path,
							path=edge[0][0],
							out_path=edge[0][1],
							pragmatic_plugin_path=shared.pragmatic_plugin_path,
							meta_path=shared.meta_path,
							preamble_path=shared.pragmatic_preamble_path
							)

@typechecked
def store_edge_hashes(graph: nx.DiGraph, edge: object):
	node_attributes = nx.get_node_attributes(graph, 'metadata')
	# Save edge hashes
	obj_hash = utility.hash_file(resolve_meta_paths(edge[0][1]))
	edge[1]['metadata']['hash'] = obj_hash
	input_hashes = []
	nodes_to_object = get_nodes_leading_to_node(graph, edge[0][1])[1:]
	for node in nodes_to_object:
		input_hashes.append(node_attributes[node]['hash'])
	edge[1]['metadata']['input_hashes'] = input_hashes

	# Save node hash
	node_attributes[edge[0][1]]['hash'] = obj_hash

@typechecked
def generate_object_command(graph: nx.DiGraph, edge: object) -> bool:
	did_process = False
	node_attributes = nx.get_node_attributes(graph, 'metadata')
	nodes_to_object = get_nodes_leading_to_node(graph, edge[0][1])[1:]

	# Base command
	command = (
		'{{clang_path}} -c {{path}} -o {{out_path}} '
		'{options} '
		'-fplugin={{pragmatic_plugin_path}} -DPRAGMATIC_FILE_PATH=\"{{meta_path}}\" '
		'--include={{preamble_path}}')

	# Collect compiler settings from nodes leading to object file
	compiler_options = []
	for node in nodes_to_object:
		node_meta = node_attributes[node]
		compiler_options.extend(interpret_metadata(node_meta))

	# Preformat compile command without filling in default paths
	preformatted_cmd = command.format(options=' '.join(compiler_options))
	if 'command' not in edge[1]['metadata'] or edge[1]['metadata']['command'] != preformatted_cmd:
		edge[1]['metadata']['command'] = preformatted_cmd
		did_process = True
	return did_process

@typechecked
def check_edge_conditions(graph: nx.DiGraph, edge: object) -> bool:
	node_attributes = nx.get_node_attributes(graph, 'metadata')
	return ('hash' not in node_attributes[edge[0][1]] or
			'hash' not in edge[1]['metadata'] or
			node_attributes[edge[0][1]]['hash'] != edge[1]['metadata']['hash'] or
			not check_edge_input_hashes(graph, edge))

@typechecked
def iterate() -> None:
	did_process = True
	iteration_count = 0

	while did_process:
		iteration_count += 1
		did_process = False

		# Load meta file
		exists: bool = load_meta()
		if not exists:
			success = compile_source_file(shared.initial_path)
			if not success:
				print('Initial compile failed')
			load_meta()

		# Load
		graph = load_graph()

		# Check hashes & set runtime valid_hash flags
		update_hashes(graph)


		# Get targets
		targets = get_nodes_by_extension(graph, '.exe')

		# Sort nodes topologically
		topological_generations = get_topological_layers(graph)

		# Collect nodes for each target
		for target in targets:
			# Get all nodes connected to target
			nodes_to_target = get_nodes_leading_to_node(graph, target)

			# Filter topological nodes by target
			sorted_nodes = []
			for layer_of_nodes in topological_generations:
				sorted_nodes.append(list(set(layer_of_nodes) & set(nodes_to_target)))

			# Get edges in order of sorted_nodes
			collected_edges = []
			for edge, attribute in graph.edges().items():
				for sorted_layer_of_nodes in sorted_nodes:
					if edge[1] in sorted_layer_of_nodes:
						collected_edges.append((edge, attribute))


			# Generate commands for edges
			for edge in collected_edges:
				if edge[1]['relation'] == 'object':
					did_process = did_process or generate_object_command(graph, edge)
			
			# Return graph meta to meta file
			retrieve_graph_meta(graph)
			save_meta()

			# Run edge commands
			for edge in collected_edges:
				# Check rebuild conditions
				if (check_edge_conditions(graph, edge)):
					if edge[1]['relation'] == 'object':
						# Instantiate command template
						if 'command' not in edge[1]['metadata']:
							continue
						command = instantiate_command(edge[1]['metadata']['command'], edge)
						success = run_command(command)
						if success:
							store_edge_hashes(graph, edge)

							# Return graph meta to meta file
							retrieve_graph_meta(graph)
							save_meta()
							did_process = True

			# Collect link edges
			link_edges = []
			for edge in collected_edges:
				if edge[1]['relation'] == 'link':
					link_edges.append(edge)

			default_output = link_edges[0][0][1]

			# Check if product exists
			node_runtime_attributes = nx.get_node_attributes(graph, 'runtime')
			target_exists = node_runtime_attributes[default_output]['file_exists']		

			# Check if all edges have the same output hash
			node_attributes = nx.get_node_attributes(graph, 'metadata')
			all_output_hashes_correct = True
			inputs = []
			if not target_exists:
				all_output_hashes_correct = False
			else:
				for edge in link_edges:
					if node_attributes[edge[0][1]]['hash'] != utility.hash_file(resolve_meta_paths(edge[0][1])):
						all_output_hashes_correct = False
						inputs.append(edge[0][0])	

			# Check if all link edges have requirements satisfied
			node_attributes = nx.get_node_attributes(graph, 'metadata')
			all_hashes_correct = True
			inputs = []
			for edge in link_edges:
				if 'hash' not in node_attributes[edge[0][0]]:
					all_hashes_correct = False
				elif node_attributes[edge[0][0]]['hash'] != utility.hash_file(resolve_meta_paths(edge[0][0])):
					all_hashes_correct = False
				inputs.append(edge[0][0])
			if len(link_edges) > 0 and all_hashes_correct and (not target_exists or not all_output_hashes_correct):
				# Generate link command template
				command = '{clang_path} {inputs} -o {out_path}'
				command = command.format(clang_path=shared.clang_path, inputs=' '.join(inputs), out_path=default_output)

				success = run_command(command)
				if success:
					for edge in link_edges:
						store_edge_hashes(graph, edge)

					# Return graph meta to meta file
					retrieve_graph_meta(graph)
					save_meta()
					did_process = True


	print(f'Iteration count : {iteration_count}')
	