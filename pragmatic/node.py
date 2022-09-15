from __future__ import annotations
from pathlib import Path

from autoslot import Slots

from pragmatic import shared

from . import graph
from . import utility

extenion_colors = {
	'.hpp': 0,
	'.cpp': 1,
	'.ii': 2,
	'.obj': 3,
	'.exe': 4
}

class Node(Slots):
	def __init__(self, path: Path):
		# convert string to Path
		if isinstance(path, str):
			path = Path(path)

		self.path: Path = path
		self.parents: list[Node] = []
		self.children: list[Node] = []
		self.associated: list[Node] = []

		self.filename: str = path.stem
		self.extension: str = path.suffix
		self.dir: Path = path.parent

		self.command: str = ''
		self.hash: str = ''

		graph.nodes.append(self)

	# Properties

	@property
	def is_hash_valid(self) -> bool:
		return self.path.exists() and utility.hash_file(self.path.resolve()) == self.hash

	@property
	def is_parents_valid(self):
		return all(parent.is_valid for parent in self.parents)

	@property
	def is_valid(self) -> bool:
		return self.is_hash_valid and self.is_parents_valid

	# Methods

	def CalculateHash(self):
		self.hash = utility.hash_file(self.path)

	# Node edges

	def add_parents(self, parents: list[Node]):
		# If passed parents isn't a list, just one parent, convert to list
		if type(parents) is not list: parents = [ parents ]
		# If parent is already in list, do nothing
		for parent in parents:
			if parent not in self.parents:
				self.parents.append(parent)
				parent.children.append(self)

	def add_children(self, children: list[Node]):
		# If passed parents isn't a list, just one parent, convert to list
		if type(children) is not list: children = [ children ]
		# If parent is already in list, do nothing
		for child in children:
			if child not in self.children:
				self.children.append(child)
				child.parents.append(self)

	# Visual serialization

	def serialize_node(self):
		return { 'id': str(self.path), 'group': extenion_colors[self.extension] }
	
	def serialize_links(self):
		links = []
		for child in self.children:
			links.append({ 'source': str(self.path), 'target': str(child.path), 'value': 1 })
		return links