import json
import hashlib
import subprocess
from pathlib import Path

import networkx as nx
from typeguard import typechecked

from . import shared

#region Python utils

def join_list_of_tuples(tuples: list[tuple[any, any]]):
	return set(elem for sub_tuple in tuples for elem in sub_tuple)

#endregion

#region Hash

@typechecked
def hash_file(file_path: str | Path) -> str:
	if type(file_path) is Path:
		file_path = str(file_path)
	BLOCK_SIZE = 65536
	hasher = hashlib.sha1()
	with open(file_path, 'rb') as file_handle:
		buf = file_handle.read(BLOCK_SIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = file_handle.read(BLOCK_SIZE)
	return hasher.hexdigest()

@typechecked
def hash_str(str: str) -> str:
	hasher = hashlib.sha1()
	hasher.update(str.encode('utf-8'))
	return hasher.hexdigest()

#endregion

#region Save & load

@typechecked
def load_meta() -> bool:
	success: bool = False
	if shared.meta_path.exists():
		with open(shared.meta_path, 'r', encoding='utf-8') as meta_file:
			shared.meta = json.load(meta_file)
		success = True

	if not success:
		return_code = 1
		count = 0
		while return_code != 0:
			return_code = run_syntax_only(shared.initial_path)
			if return_code == 42:
				print('Initial compile requires different language options')
			else:
				print('Initial compile failed')
			load_meta()

			count = count + 1
			if count == 5:
				print(f'Could not run syntax only compile on initial file in {count} iterations.')
				return False
	return True

@typechecked
def save_meta(sort_keys=False) -> None:
	with open(shared.meta_path, 'w') as meta_file:
		json.dump(shared.meta, meta_file, indent=4, sort_keys=sort_keys)

#endregion

#region Paths

@typechecked
def resolve_meta_paths(meta_path: str) -> Path:
	return shared.initial_path_dir.joinpath(meta_path)

#endregion

#region Subprocess & execution

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
def run_syntax_only(path: Path) -> int:
	return_code = execute(path, None, '-fsyntax-only')
	return return_code

@typechecked
def run_build(edge: tuple[str, str]) -> int:
	return_code = execute(edge[0], edge[1], '-c')
	return return_code

@typechecked
def run_link(graph: nx.DiGraph, link_edges):
	link_targets: set[str] = set()
	for link_edge in link_edges:
		link_targets.add(link_edge[1])

	link_edges: dict[str, set[set[str, str]]] = dict()
	for edges in graph.edges():
		if edges[1] in link_targets:
			if edges[1] not in link_edges:
				link_edges[edges[1]] = set()
			link_edges[edges[1]].add(edges)

	for key, value in link_edges.items():
		objects = join_list_of_tuples(value)
		objects.remove(key)

		return_code = execute_link(objects, key)

	pass

def execute_link(in_paths: set[str], out_path: str) -> int:
	rel_in_paths = []
	for path in in_paths:
		rel_in_paths.append(str(shared.initial_path_dir.joinpath(path).relative_to(shared.initial_path_dir)))
	rel_out_path = shared.initial_path_dir.joinpath(out_path).relative_to(shared.initial_path_dir)

	command = ' '.join([
		f'{shared.clang_path} {" ".join(rel_in_paths)} -o {rel_out_path}'	# Clang_path source.o target.exe
	])

	if all(Path(rel_in_path).is_file for rel_in_path in rel_in_paths):
		return_code = run_subprocess(command, shared.initial_path_dir)
		return return_code
	else: return 1

@typechecked
def execute(in_path: Path|str, out_path: Path|str=None, options: list[str]|str=[]) -> int:
	if type(options) == str: options = [options]
	rel_in_path = shared.initial_path_dir.joinpath(in_path).relative_to(shared.initial_path_dir)
	rel_out_path = shared.initial_path_dir.joinpath(rel_in_path.with_suffix(".o") if out_path == None else out_path).relative_to(shared.initial_path_dir)
	
	options = ' '.join(options) 
	command = ' '.join([
		f'{shared.clang_path} {options} {rel_in_path} -o {rel_out_path}',	# Clang_path -c source.cpp -o source.o
		f'-fplugin={shared.pragmatic_plugin_path}',							# -fplugin=.../pragmatic/pragmatic_plugin/build/PragmaticPlugin.dll
		f'-DPRAGMATIC_FILE_PATH=\"{shared.meta_path}\"',					# -DPRAGMATIC_FILE_PATH="path/to/meta.json"
		f'--include={shared.pragmatic_preamble_path}',						# --include=.../pragmatic/include/preamble.hpp
	])

	if shared.meta is not None:
		command += ' ' + ' '.join(interpret_metadata(shared.meta['graphs'][0]['nodes'][str(rel_in_path)]['metadata']))
	
	if rel_in_path.is_file and rel_in_path.suffix == '.cpp':
		return_code = run_subprocess(command, shared.initial_path_dir)
		return return_code
	else: return 1

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

#endregion