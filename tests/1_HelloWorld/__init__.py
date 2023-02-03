import unittest
from pathlib import Path

from pragmatic import pragmatic, utility
from tests.test_runner import delete_files

from click.testing import CliRunner


class test_HelloWorld(unittest.TestCase):
	def setUp(self):
		delete_files('tests/1_HelloWorld/meta.json')
		delete_files('tests/1_HelloWorld/*.o')
		delete_files('tests/1_HelloWorld/*.exe')

		self.path = str(Path("tests/1_HelloWorld/Hello.cpp").absolute())

		pragmatic.initialize()

	def test_build(self):
		runner = CliRunner()
		result = runner.invoke(pragmatic.cli, ['build', self.path])
		
		self.assertEqual(0, result.exit_code, 'build failed')
		self.assertEqual(pragmatic.shared.iteration_count, 2, 'build did unneccessary work')

		# run
		code, str = utility.run_subprocess('tests/1_HelloWorld/Hello.exe', Path().cwd())
		self.assertEqual(0, code, 'runtime error')

	def test_rebuild(self):
		runner = CliRunner()
		result = runner.invoke(pragmatic.cli, ['build', self.path])
		self.assertEqual(0, result.exit_code, 'build failed')
		self.assertEqual(pragmatic.shared.iteration_count, 2, 'build did unneccessary work')

		pragmatic.initialize()
		runner = CliRunner()
		result = runner.invoke(pragmatic.cli, ['build', self.path])
		self.assertEqual(0, result.exit_code, 'build failed')
		self.assertEqual(pragmatic.shared.iteration_count, 1, 'build did unneccessary work')