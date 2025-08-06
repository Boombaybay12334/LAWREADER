import networkx as nx
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()
class GraphTraversal:
    def __init__(self, graph_path: str = os.getenv("GRAPH_PATH")):
        """
        Initialize the graph traversal with the legal graph.
        
        Args:
            graph_path: Path to the legal graph pickle file
        """
        self.graph_path = "law_graphTest.gpickle"
        self.graph = None
        self._load_graph()
    
    def _load_graph(self):
        """Load the legal graph from pickle file."""
        if not os.path.exists(self.graph_path):
            raise FileNotFoundError(f"Graph file not found: {self.graph_path}")
        
        self.graph = nx.read_gpickle(self.graph_path)
        print(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def expand_context(self, scenario_id: str) -> Dict[str, Any]:
        """
        Collect all legally relevant context from a matched scenario.
        
        Args:
            scenario_id: The ID of the matched scenario node
            
        Returns:
            Dictionary containing scenario, principles, and articles data
        """
        if scenario_id not in self.graph.nodes:
            raise ValueError(f"Scenario ID '{scenario_id}' not found in graph")
        
        context = {
            'scenario': {},
            'principles': [],
            'articles': [],
            'scenario_id': scenario_id
        }
        
        # Get scenario data
        scenario_data = self.graph.nodes[scenario_id]
        if scenario_data.get('type') != 'scenario':
            print(f"Warning: Node {scenario_id} is not a scenario node (type: {scenario_data.get('type')})")
        
        context['scenario'] = {
            'id': scenario_id,
            'example': scenario_data.get('example', ''),
            'type': scenario_data.get('type', ''),
            'all_data': scenario_data
        }
        
        # Find connected principle nodes via 'supports' edges
        principle_nodes = []
        for neighbor in self.graph.neighbors(scenario_id):
            edge_data = self.graph.get_edge_data(scenario_id, neighbor)
            if edge_data and edge_data.get('type') == 'supports':
                neighbor_data = self.graph.nodes[neighbor]
                if neighbor_data.get('type') == 'principle':
                    principle_nodes.append((neighbor, neighbor_data))
        
        print(f"Found {len(principle_nodes)} principle nodes connected to scenario {scenario_id}")
        
        # Process principle nodes
        for principle_id, principle_data in principle_nodes:
            principle_info = {
                'id': principle_id,
                'text': principle_data.get('text', ''),
                'type': principle_data.get('type', ''),
                'all_data': principle_data
            }
            context['principles'].append(principle_info)
        
        # Find connected article nodes via 'explains' edges from principles
        article_nodes = []
        for principle_id, _ in principle_nodes:
            for neighbor in self.graph.neighbors(principle_id):
                edge_data = self.graph.get_edge_data(principle_id, neighbor)
                if edge_data and edge_data.get('type') == 'explains':
                    neighbor_data = self.graph.nodes[neighbor]
                    if neighbor_data.get('type') == 'article':
                        # Avoid duplicates
                        if neighbor not in [article[0] for article in article_nodes]:
                            article_nodes.append((neighbor, neighbor_data))
        
        print(f"Found {len(article_nodes)} article nodes connected to principles")
        
        # Process article nodes
        for article_id, article_data in article_nodes:
            article_info = {
                'id': article_id,
                'title': article_data.get('title', ''),
                'description': article_data.get('description', ''),
                'type': article_data.get('type', ''),
                'all_data': article_data,
                'number': article_data.get('number', ''),
            }
            context['articles'].append(article_info)
        
        return context
    
    def get_related_scenarios(self, scenario_id: str) -> List[Dict[str, Any]]:
        """
        Find scenarios related to the given scenario via 'related' edges.
        
        Args:
            scenario_id: The ID of the scenario node
            
        Returns:
            List of related scenario dictionaries
        """
        if scenario_id not in self.graph.nodes:
            return []
        
        related_scenarios = []
        for neighbor in self.graph.neighbors(scenario_id):
            edge_data = self.graph.get_edge_data(scenario_id, neighbor)
            if edge_data and edge_data.get('type') == 'related':
                neighbor_data = self.graph.nodes[neighbor]
                if neighbor_data.get('type') == 'scenario':
                    related_scenarios.append({
                        'id': neighbor,
                        'example': neighbor_data.get('example', ''),
                        'type': neighbor_data.get('type', ''),
                        'all_data': neighbor_data
                    })
        
        return related_scenarios
    
    def get_full_context(self, scenario_id: str) -> Dict[str, Any]:
        """
        Get complete context including related scenarios.
        
        Args:
            scenario_id: The ID of the scenario node
            
        Returns:
            Dictionary with full context including related scenarios
        """
        context = self.expand_context(scenario_id)
        context['related_scenarios'] = self.get_related_scenarios(scenario_id)
        return context
    
    def analyze_node_connections(self, node_id: str) -> Dict[str, Any]:
        """
        Analyze all connections of a given node for debugging.
        
        Args:
            node_id: The ID of the node to analyze
            
        Returns:
            Dictionary with connection analysis
        """
        if node_id not in self.graph.nodes:
            return {'error': f"Node {node_id} not found"}
        
        node_data = self.graph.nodes[node_id]
        connections = {
            'node_id': node_id,
            'node_type': node_data.get('type', 'unknown'),
            'node_data': node_data,
            'connections': []
        }
        
        for neighbor in self.graph.neighbors(node_id):
            edge_data = self.graph.get_edge_data(node_id, neighbor)
            neighbor_data = self.graph.nodes[neighbor]
            
            connections['connections'].append({
                'neighbor_id': neighbor,
                'neighbor_type': neighbor_data.get('type', 'unknown'),
                'edge_type': edge_data.get('type', 'unknown') if edge_data else 'no_type',
                'edge_data': edge_data
            })
        
        return connections


# Standalone function for easy LLM code generation
def expand_context(scenario_id: str, graph_path: str = "law_graphTest.gpickle") -> Dict[str, Any]:
    """
    Simple interface function to expand context from a scenario.
    
    Args:
        scenario_id: The ID of the matched scenario node
        graph_path: Path to the legal graph
        
    Returns:
        Dictionary containing scenario, principles, and articles data
    """
    traversal = GraphTraversal(graph_path)
    return traversal.expand_context(scenario_id)


if __name__ == "__main__":
    # Test the graph traversal
    try:
        traversal = GraphTraversal()
        
        # Get some scenario nodes to test
        scenario_nodes = [
            node_id for node_id, data in traversal.graph.nodes(data=True)
            if data.get('type') == 'scenario'
        ]
        
        if scenario_nodes:
            test_scenario = scenario_nodes[0]  # Use first scenario for testing
            print(f"Testing with scenario: {test_scenario}")
            
            # Analyze connections first
            analysis = traversal.analyze_node_connections(test_scenario)
            print(f"\nNode Analysis:")
            print(f"Node Type: {analysis['node_type']}")
            print(f"Number of connections: {len(analysis['connections'])}")
            
            connection_types = {}
            for conn in analysis['connections']:
                edge_type = conn['edge_type']
                neighbor_type = conn['neighbor_type']
                key = f"{edge_type} -> {neighbor_type}"
                connection_types[key] = connection_types.get(key, 0) + 1
            
            print("Connection types:")
            for conn_type, count in connection_types.items():
                print(f"  {conn_type}: {count}")
            
            # Test context expansion
            print(f"\nExpanding context for scenario: {test_scenario}")
            context = traversal.expand_context(test_scenario)
            
            print(f"\nContext Summary:")
            print(f"Scenario: {context['scenario']['example'][:100]}...")
            print(f"Principles: {len(context['principles'])}")
            print(f"Articles: {len(context['articles'])}")
            
            # Print some details if available
            if context['principles']:
                print(f"\nFirst principle: {context['principles'][0]['text'][:100]}...")
            
            if context['articles']:
                print(f"\nFirst article: {context['articles'][0]['title']}")
                if context['articles'][0]['layman_summary']:
                    print(f"Summary: {context['articles'][0]['layman_summary'][:100]}...")
            
            # Test related scenarios
            related = traversal.get_related_scenarios(test_scenario)
            print(f"\nRelated scenarios: {len(related)}")
            
        else:
            print("No scenario nodes found in the graph")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the law_graphfinal.gpickle file exists")