

import json
import subprocess
import os
import pathlib

pragmatic_package_dir = os.path.dirname(__file__)
data_dir = f'{pragmatic_package_dir}/data'
clang_exe = f'{data_dir}/LLVM/bin/clang.exe'
pragmatic_meta_macro = 'PRAGMATIC_FILE_PATH'
pragmatic_dll = f'{data_dir}/PragmaticPlugin/PragmaticPlugin.dll'

class graph_build:
	def preprocess_file(file_path):
		file_name = pathlib.Path(file_path).stem
		source_dir = pathlib.Path(file_path).parent
		flags = ['-E']
		output_path = f'{source_dir}/{file_name}.ii'
		subprocess.run(f'{clang_exe} {" ".join(flags)} -fplugin={pragmatic_dll} {file_path} -o {output_path}')
		return output_path


	def build_file(file_path):
		file_name = pathlib.Path(file_path).stem
		source_dir = pathlib.Path(file_path).parent
		flags = ['-c']
		output_path = f'{source_dir}/{file_name}.obj'
		subprocess.run(f'{clang_exe} {" ".join(flags)} {file_path} -o {output_path}')
		return output_path

	def link(paths, name = None):
		file_name = name if name != None else pathlib.Path(paths[0]).stem
		source_dir = pathlib.Path(paths[0]).parent
		flags = ['-c', '-fuse-ld=lld']
		output_path = f'{source_dir}/{file_name}.exe'
		subprocess.run(f'{clang_exe} {" ".join(flags)} {" ".join(paths)} -o {output_path}')
		return output_path