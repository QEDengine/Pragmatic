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



def iterate_graph():
	# Load meta file
	exists: bool = load_meta()
	if not exists:
		success = compile_source_file(shared.initial_path)
		load_meta()

	# Build object files
	for edge in shared.meta['graph']['edges']:
		if edge['relation'] == 'object':
			source_path = resolve_meta_paths(edge['source'])
			# If hashes match, do not recompile
			if 'hash' in shared.meta['graph']['nodes'][edge['source']]['metadata'] and 'hash' in shared.meta['graph']['nodes'][edge['target']]['metadata']:
				if shared.meta['graph']['nodes'][edge['source']]['metadata']['hash'] == utility.hash_file(source_path):
					if shared.meta['graph']['nodes'][edge['target']]['metadata']['hash'] == utility.hash_file(resolve_meta_paths(edge['target'])):
						print(f'Source {edge["source"]} is up to date')
						continue
			success = compile_source_file(source_path, shared.meta['graph']['nodes'][edge['source']]['metadata'])
			print(f'Build {"succeded" if success == 1 else "failed"} : {edge["source"]}')
			if success:
				# Hash source file
				s_hash = utility.hash_file(source_path)
				shared.meta['graph']['nodes'][edge['source']]['metadata']['hash'] = s_hash
				# Hash object file
				o_hash = utility.hash_file(resolve_meta_paths(edge['target']))
				shared.meta['graph']['nodes'][edge['target']]['metadata']['hash'] = o_hash

	# Link
	# Get targets
	targets = []
	for edge in shared.meta['graph']['edges']:
		if edge['target'] not in targets and edge['relation'] == 'link':
			targets.append(edge['target'])
	for target in targets:
		can_build_target = True
		objects_to_link = []
		object_hashes = ''
		for edge in shared.meta['graph']['edges']:
			if edge['target'] == target:
				if shared.meta['graph']['nodes'][edge['source']]['metadata']['hash'] != utility.hash_file(resolve_meta_paths(edge['source'])):
					can_build_target = False
				else:
					objects_to_link.append(resolve_meta_paths(edge['source']))
					object_hashes += shared.meta['graph']['nodes'][edge['source']]['metadata']['hash']
		if can_build_target and len(objects_to_link) > 0:
			# Check hashes
			if resolve_meta_paths(target).exists() and 'hash' in shared.meta['graph']['nodes'][target]['metadata']:
				if 'input_hash' in shared.meta['graph']['nodes'][target]['metadata'] and shared.meta['graph']['nodes'][target]['metadata']['input_hash'] == utility.hash_str(object_hashes):
					if shared.meta['graph']['nodes'][target]['metadata']['hash'] == utility.hash_file(resolve_meta_paths(target)):
						print(f'Target {target} is up to date')
						continue

			print(f'Building target : {target}')
			success = link_files(objects_to_link, resolve_meta_paths(target))
			if success:
				# Hash target
				t_hash = utility.hash_file(resolve_meta_paths(target))
				shared.meta['graph']['nodes'][target]['metadata']['hash'] = t_hash
				# Hash input names
				shared.meta['graph']['nodes'][target]['metadata']['input_hash'] = utility.hash_str(object_hashes)
			

	save_meta()