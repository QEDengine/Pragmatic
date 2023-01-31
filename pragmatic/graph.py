from pathlib import Path
from typing import Any
from typing import Tuple

from typeguard import typechecked
import networkx as nx

from . import shared
from . import utility

#region Save & load graph

@typechecked
def load_graph() -> nx.DiGraph:
	utility.load_meta()
	data = shared.meta['graphs'][0]
	graph = nx.DiGraph()
	for node in data['nodes']:
		graph.add_node(node, metadata=data['nodes'][node]['metadata'])
	for edge in data['edges']:
		graph.add_edge(edge['source'], edge['target'], relation=edge['relation'], metadata=edge['metadata'])
	return graph

@typechecked
def retrieve_meta_from_graph(graph: nx.DiGraph) -> None:
	node_metadata_attributes = nx.get_node_attributes(graph, 'metadata')
	for node in shared.meta['graphs'][0]['nodes']:
		shared.meta['graphs'][0]['nodes'][node]['metadata'] = node_metadata_attributes[node]

#endregion

@typechecked
def check_hashes(graph: nx.DiGraph) -> set[str]:
	updated_nodes = set()
	for node, attribute in graph.nodes().items():
		# Get absolute path
		node_path = utility.resolve_meta_paths(node)

		# Check file exists
		if node_path.exists():
			node_file_hash = utility.hash_file(node_path)
		else:
			updated_nodes.add(node)

		# Initialize metadata attribute
		if 'metadata' not in attribute:
			attribute['metadata'] = {}

		# Update hashes
		if ('hash' not in attribute['metadata'] or node_file_hash != attribute['metadata']['hash']):
			attribute['metadata']['hash'] = node_file_hash
			updated_nodes.add(node)
	return updated_nodes

@typechecked
def get_edges_from_node(graph: nx.DiGraph, node: str) -> list[Tuple[Any, Any]]:
    edges = []
    next_nodes = [node]
    while next_nodes:
        current_node = next_nodes.pop(0)
        for successor in graph.successors(current_node):
            edges.append((current_node, successor))
            next_nodes.append(successor)
    return edges

def topological_sort(graph: nx.DiGraph) -> list[Tuple[Any, Any]]:
	sorted_nodes = list(nx.topological_sort(graph))
	return [(sorted_nodes[i], sorted_nodes[i + 1]) for i in range(len(sorted_nodes) - 1)]

@typechecked
def iterate() -> None:
	did_process = True
	iteration_count = 0

	link_edges = set()

	while did_process:
		iteration_count += 1
		did_process = False

		# Load meta file & compile initial file
		exists: bool = utility.load_meta()
		if not exists: exit(1)

		graph = load_graph()

		# Get edges to update
		updated_nodes = check_hashes(graph)

		edges_to_update = set()
		edge: tuple[str, str]
		for edge, attribute in graph.edges().items():
			edge_nodes = set()
			edge_nodes.add(edge[0])
			edge_nodes.add(edge[1])
			for define in attribute['metadata']['defined']:
				edge_nodes.add(define)

			intersection = edge_nodes & updated_nodes
			if len(intersection) > 0:
				edges_to_update.add(edge)

		# Sort edges
		subgraph = graph.edge_subgraph(edges_to_update)
		sorted_paths = topological_sort(subgraph)

		edge_relation = nx.get_edge_attributes(graph, 'relation')
		edge_metadata = nx.get_edge_attributes(graph, 'metadata')
		node_metadata = nx.get_node_attributes(graph, 'metadata')
		for edge in sorted_paths:
			print(edge_relation[edge])
			print(edge_metadata[edge])

			match edge_relation[edge]:
				case 'include':
					did_process = True
					node_metadata[edge[1]]['hash'] = 0
				case 'build':
					did_process = True
					utility.run_build(edge)
					check_hashes(graph.subgraph(edge))
				case 'link':
					link_edges.add(edge)
		
		retrieve_meta_from_graph(graph)
		utility.save_meta()

	utility.run_link(graph, link_edges)
	all_link_edges = utility.join_list_of_tuples(link_edges)
	check_hashes(graph.subgraph(all_link_edges))

	retrieve_meta_from_graph(graph)
	utility.save_meta()

	print(f'Iteration count : {iteration_count}')
	