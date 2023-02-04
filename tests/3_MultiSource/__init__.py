import unittest
from pathlib import Path

from pragmatic import pragmatic, utility
from tests.test_runner import delete_files

from click.testing import CliRunner

class test_MultiSource(unittest.TestCase):
	def setUp(self):
		delete_files('tests/3_MultiSource/meta.json')
		delete_files('tests/3_MultiSource/*.o')
		delete_files('tests/3_MultiSource/*.exe')

		self.path = str(Path("tests/3_MultiSource/Main.cpp").absolute())

		pragmatic.initialize()

	def test_build(self):
		runner = CliRunner()
		result = runner.invoke(pragmatic.cli, ['build', self.path])
		
		self.assertEqual(0, result.exit_code, 'build failed')
		self.assertEqual(pragmatic.shared.iteration_count, 3, 'build did unneccessary work')

		# run
		code, str = utility.run_subprocess('tests/3_MultiSource/MultiSource.exe', Path().cwd())
		self.assertEqual(0, code, 'runtime error')