import unittest
from pathlib import Path
import subprocess

from typeguard import typechecked

environment_path = 'tests/test_environment'

@typechecked
def create_virtual_environment(path: Path|str) -> bool:
	if type(path) == str: path = Path(path)

	if (not Path(path).exists()):
		print(f'Creating test environment at {path}')
		proc = subprocess.run(f'python -m venv {path}', shell=True, stdout=subprocess.PIPE)
		print(f'Created virtual environment with exit code {proc.returncode}')
		return proc.returncode == 0
	else: return True

def run_in_venv(path, command):
	process = subprocess.Popen([f'{path}\\Scripts\\activate.bat && python {command}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	lines = process.stdout.readlines()
	for line in lines:
		print(line.decode('ascii'))
	process.stdin.close()
	print('Waiting for venv python to exit')
	process.wait()
	print(f'{command} finished with return code {process.returncode}')

class PragmaticTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
    def addSkip(self, test, reason):
        unittest.TestResult.addSkip(self, test, reason)

class PragmaticTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return PragmaticTestResult(self.stream, self.descriptions, self.verbosity)

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover('.')
    PragmaticTestRunner().run(suite)