from os import path
import subprocess
from subprocess import PIPE
import pathlib
import os

cmake_build_command = 'cmake --build . --config MinSizeRel'
subprocess.run(f'cd Build && {cmake_build_command}', shell=True)