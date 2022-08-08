from os import path
import subprocess
import pathlib
import os
import shutil

if not pathlib.Path('Install').exists():
	os.makedirs('Install')

cmake_install_command = 'cmake --install . --config MinSizeRel --prefix "./../install"'
subprocess.run(f'cd Build && {cmake_install_command}', shell=True)

shutil.copyfile('Build\MinSizeRel\lib\clang.lib', 'Install\lib\clang.lib')
shutil.copyfile('Build\MinSizeRel\lib\clang.exp', 'Install\lib\clang.exp')