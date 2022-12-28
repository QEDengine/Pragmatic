from pathlib import Path
import subprocess
import json

from typeguard import typechecked

from . import shared
from . import utility

def load_meta() -> bool:
	if shared.meta_path.exists():
		with open(shared.meta_path, 'r') as meta_file:
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
			print(output.strip())
	return process.poll()


def interpret_metadata(metadata: object):
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



def iterate_graph():
	# Load meta file
	exists: bool = load_meta()
	if not exists:
		success = compile_source_file(shared.initial_path)
		load_meta()

	# Calculate hashes
	for edge in shared.meta['graph']['edges']:
		if edge['relation'] == 'object':
			success = compile_source_file(Path(edge['source']), shared.meta['graph']['nodes'][edge['source']]['metadata'])
			print(f'Build {"succeded" if success == 1 else "failed"} : {edge["source"]}')


	# for node in shared.meta['graph']['nodes']:
	# 	resolved_node_path: Path = resolve_meta_paths(node)
	# 	if resolved_node_path.exists():
	# 		hash = utility.hash_file(resolved_node_path)
	# 		shared.meta['graph']['nodes'][node]['metadata']['hash'] = hash

	# 		if resolved_node_path.suffix == '.cpp':
	# 			success = compile_source_file(shared.initial_path, shared.meta['graph']['nodes'][node]['metadata'])
			


	save_meta()
	# Run edges