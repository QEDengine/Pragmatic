from os import path
import subprocess
from subprocess import PIPE
import pathlib
import os

# Set current working directory to this file's directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))
cwd = os.getcwd()
print("cwd : " + cwd)

if not pathlib.Path('./../Build').exists():
	os.makedirs('./../Build')

cmake_configure_command = 'cmake ./.. -G "Visual Studio 16 2019"'
subprocess.run(f'cd ./../Build && {cmake_configure_command}', shell=True)