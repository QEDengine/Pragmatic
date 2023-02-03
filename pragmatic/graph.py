from pathlib import Path
from typing import Any
from typing import Tuple

from typeguard import typechecked
import networkx as nx
import jsonpatch

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
			continue

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

@typechecked
def sort_edges(graph: nx.DiGraph):
	relation_order = {'include': 1, 'build': 2, 'link': 3}
	return sorted(graph.edges(), key=lambda x: relation_order[graph.edges[x]['relation']])

@typechecked
def iterate() -> tuple[bool, int]:
	success = True
	did_process = True

	link_edges = set()

	while did_process:
		shared.iteration_count += 1
		did_process = False

		# Load meta file & compile initial file
		exists: bool = utility.load_meta()
		if not exists: exit(1)

		graph = load_graph()

		# Get edges to update
		updated_nodes = check_hashes(graph)

		# Get edges to be updated
		edges_to_update = []
		for node in updated_nodes:
			edges_to_update.append(get_edges_from_node(graph, node))
		edges_to_update = utility.join_list_of_tuples(edges_to_update)

		sorted_edges = sort_edges(graph.edge_subgraph(edges_to_update))

		# Execute edges by relation type
		edge_relation = nx.get_edge_attributes(graph, 'relation')
		node_metadata = nx.get_node_attributes(graph, 'metadata')
		for edge in sorted_edges:
			if edge in edge_relation:
				match edge_relation[edge]:
					case 'include':
						did_process = True
						node_metadata[edge[1]]['hash'] = 0
						check_hashes(graph.subgraph(edge[0]))
					case 'build':
						did_process = True
						utility.run_build(edge)
						check_hashes(graph.subgraph(edge))
					case 'link':
						link_edges.add(edge)

		retrieve_meta_from_graph(graph)
		utility.save_meta()
		if shared.iteration_count > 10:
			success = False
			break

	utility.run_link(graph, link_edges)
	all_link_edges = utility.join_list_of_tuples(link_edges)
	check_hashes(graph.subgraph(all_link_edges))

	retrieve_meta_from_graph(graph)
	utility.save_meta()

	print(f'Iteration count : {shared.iteration_count}')
	return (success, shared.iteration_count)
	