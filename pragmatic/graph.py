from __future__ import annotations
from pathlib import Path
import json

from autoslot import Slots

nodes: list[Node] = []

class Node(Slots):
	def __init__(self, path: str):
		global nodes

		self.path: str = path
		self.parents: list[Node] = []
		self.children: list[Node] = []

		nodes.append(self)

	def add_parents(self, parents: list[Node]):
		self.parents.extend(parents)
		for parent in parents:
			parent.children.append(self)

	def serialize_node(self):
		return { 'id': self.path, 'group': 0 }
	
	def serialize_links(self):
		links = []
		for child in self.children:
			links.append({ 'source': self.path, 'target': child.path, 'value': 1 })
		return links

def test():
	a = Node('A')
	b = Node('B')
	c = Node('C')
	c.add_parents([a, b])
	d = Node('D')
	e = Node('E')
	e.add_parents([d])
	f = Node('F')
	f.add_parents([c, e])

	serialized = {}
	serialized['nodes'] = []
	for node in nodes:
		serialized['nodes'].append(node.serialize_node())

	serialized['links'] = []
	for node in nodes:
		serialized['links'].extend(node.serialize_links())

	return json.dumps(serialized, indent=4)
