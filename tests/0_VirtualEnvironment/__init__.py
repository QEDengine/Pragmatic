import unittest
from pathlib import Path

from tests.test_runner import create_virtual_environment, run_in_venv, environment_path

class test_HelloWorld(unittest.TestCase):
	@unittest.skipIf(Path('tests/test_environment/Scripts/Python.exe').exists(), 'test environment already exists')
	def test_create_virtual_environment(self):
		success = create_virtual_environment(environment_path)
		self.assertEqual(success, True, "couldn't create virtual environment")

	@unittest.skipIf(Path('tests/test_environment/Scripts/Pragmatic.exe').exists(), 'pragmatic already built')
	def test_install(self):
		run_in_venv(str(Path(environment_path).absolute()), 'setup.py install')