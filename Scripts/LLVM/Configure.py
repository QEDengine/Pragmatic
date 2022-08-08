from os import path
import subprocess
from subprocess import PIPE
import pathlib
import os

if not pathlib.Path('Build').exists():
	os.makedirs('Build')

cmake_configure_command = 'cmake ..\External\llvm-project\llvm -G "Visual Studio 16 2019" -DLLVM_TARGETS_TO_BUILD:STRING=host -DCMAKE_BUILD_TYPE=MinSizeRel -DLLVM_OPTIMIZED_TABLEGEN=On -DLLVM_ENABLE_PROJECTS:STRING=clang -DLLVM_EXPORT_SYMBOLS_FOR_PLUGINS=ON -DLLVM_USE_CRT_RELEASE=MD -DLLVM_ENABLE_RTTI=On'
subprocess.run(f'cd Build && {cmake_configure_command}', shell=True)