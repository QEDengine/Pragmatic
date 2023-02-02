import unittest
from pathlib import Path

from pragmatic import shared
from pragmatic import graph
from pragmatic import utility

from typeguard import typechecked

@typechecked
def delete_files(globStr: str) -> None:
	import glob

	fileList = glob.glob(globStr)
	# Iterate over the list of filepaths & remove each file.
	for filePath in fileList:
		file = Path(filePath)
		if file.exists():
			file.unlink()

class test_HelloWorld(unittest.TestCase):
	def setUp(self):
		delete_files('tests/1_HelloWorld/meta.json')
		delete_files('tests/1_HelloWorld/*.o')
		delete_files('tests/1_HelloWorld/*.exe')

		path = Path("tests/1_HelloWorld/Hello.cpp").absolute()

		# set initial path given to pragmatic
		shared.initial_path_dir = path.parent
		shared.initial_path = path
		shared.meta_path = shared.initial_path_dir.joinpath(shared.META_FILE)

	def test_build(self):
		self.success, self.count = graph.iterate()
		
		self.assertEqual(True, self.success, 'build failed')
		self.assertEqual(self.count, 2, 'build did unneccessary work')

		# run
		code, str = utility.run_subprocess('tests/1_HelloWorld/Hello.exe', Path().cwd())
		self.assertEqual(0, code, 'runtime error')

	def test_rebuild(self):
		self.success, self.count = graph.iterate()
		self.assertEqual(True, self.success, 'build failed')
		self.assertEqual(self.count, 2, 'build did unneccessary work')

		self.success, self.count = graph.iterate()
		self.assertEqual(True, self.success, 'build failed')
		self.assertEqual(self.count, 1, 'build did unneccessary work')