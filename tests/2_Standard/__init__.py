import unittest
from pathlib import Path

from pragmatic import pragmatic, utility
from tests.test_runner import delete_files

from click.testing import CliRunner

class test_Standard(unittest.TestCase):
	def setUp(self):
		delete_files('tests/2_Standard/meta.json')
		delete_files('tests/2_Standard/*.o')
		delete_files('tests/2_Standard/*.exe')

		self.path = str(Path("tests/2_Standard/Standard.cpp").absolute())

		pragmatic.initialize()

	def test_build(self):
		runner = CliRunner()
		result = runner.invoke(pragmatic.cli, ['build', self.path])
		
		self.assertEqual(0, result.exit_code, 'build failed')
		self.assertEqual(pragmatic.shared.iteration_count, 2, 'build did unneccessary work')

		# run
		code, str = utility.run_subprocess('tests/2_Standard/Standard.exe', Path().cwd())
		self.assertEqual(0, code, 'runtime error')