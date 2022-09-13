import subprocess
from subprocess import PIPE
import pathlib

environment_path = 'test_environment'

def create_virtual_environment(path):
	if (not pathlib.Path(path).exists()):
		print(f'Creating test environment at {path}')
		proc = subprocess.run(f'python -m venv {path}', shell=True, stdout=PIPE)
		print(f'Created virtual environment with exit code {proc.returncode}')


def run_in_venv(path, command):
	process = subprocess.Popen([f'{path}\\Scripts\\activate.bat && python {command}'], stdin=PIPE, stdout=PIPE)
	lines = process.stdout.readlines()
	for line in lines:
		print(line.decode('ascii'))
	process.stdin.close()
	print('Waiting for venv python to exit')
	process.wait()
	print(f'{command} finished with return code {process.returncode}')



create_virtual_environment(environment_path)

run_in_venv(environment_path, 'test.py')
run_in_venv(environment_path, 'setup.py install')
run_in_venv(environment_path, 'test.py')

subprocess.run('test_environment\Scripts\Pragmatic.exe')