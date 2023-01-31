import unittest
from pathlib import Path

from pragmatic import shared
from pragmatic import graph

class test_HelloWorld(unittest.TestCase):
	def setUp(self):
		path = Path("tests\HelloWorld\Hello.cpp").absolute()

		# set initial path given to pragmatic
		shared.initial_path_dir = path.parent
		shared.initial_path = path
		shared.meta_path = shared.initial_path_dir.joinpath(shared.META_FILE)

		graph.iterate()

	def test_HelloWorld(self):
		self.assertEqual(True, True, 'incorrect default size')


		