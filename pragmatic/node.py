from __future__ import annotations
from pathlib import Path

from autoslot import Slots

from pragmatic import shared

from . import graph
from . import utility

extenion_colors = {
	'.cpp': 0,
	'.ii': 1,
	'.obj': 2,
	'.exe': 3
}

class Node(Slots):
	def __init__(self, path: Path):
		# convert string to Path
		if isinstance(path, str):
			path = Path(path)

		self.path: Path = path
		self.parents: list[Node] = []
		self.children: list[Node] = []

		self.filename: str = path.stem
		self.extension: str = path.suffix
		self.dir: Path = path.parent
		self.relative_path: Path = self.path.relative_to(shared.initial_path)

		self.command: str = ''
		self.hash: str = ''

		graph.nodes.append(self)

	# Properties

	@property
	def is_hash_valid(self) -> bool:
		return self.path.exists() and utility.hash_file(self.path.resolve()) == self.hash

	@property
	def is_valid(self) -> bool:
		return self.is_hash_valid and all(parent.is_valid for parent in self.parents)

	# Methods

	def CalculateHash(self):
		self.hash = utility.hash_file(self.path)

	# Node edges

	def add_parents(self, parents: list[Node]):
		if type(parents) is not list: parents = [ parents ]
		self.parents.extend(parents)
		for parent in parents:
			parent.children.append(self)

	def add_children(self, children: list[Node]):
		if type(children) is not list: children = [ children ]
		self.children.extend(children)
		for child in children:
			child.parents.append(self)

	# Visual serialization

	def serialize_node(self):
		return { 'id': str(self.relative_path), 'group': extenion_colors[self.extension] }
	
	def serialize_links(self):
		links = []
		for child in self.children:
			links.append({ 'source': str(self.relative_path), 'target': str(child.relative_path), 'value': 1 })
		return links