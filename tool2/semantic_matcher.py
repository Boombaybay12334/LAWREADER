# semantic_matcher.py
import networkx as nx
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional, Tuple, List, Dict
import pickle
import os
from dotenv import load_dotenv
load_dotenv()

class SemanticMatcher:
    def __init__(self, graph_path: str,
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic matcher with the legal graph and embedding model.
        
        Args:
            graph_path: Path to the legal graph pickle file
            model_name: Sentence transformer model name
        """
        self.graph_path = "law_graphTest.gpickle"
        self.model = SentenceTransformer(model_name)
        self.graph = None
        self.scenario_embeddings = None
        self.scenario_nodes = []
        
        # Load graph and prepare embeddings
        self._load_graph()
        self._prepare_scenario_embeddings()
    
    def _load_graph(self):
        """Load the legal graph from pickle file."""
        if not os.path.exists(self.graph_path):
            raise FileNotFoundError(f"Graph file not found: {self.graph_path}")
        
        self.graph = nx.read_gpickle(self.graph_path)
        print(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        print(f"Total nodes in graph: {self.graph.number_of_nodes()}")
       

        


    def _prepare_scenario_embeddings(self):
        """Extract scenario nodes and pre-compute their embeddings."""
        # Filter nodes with type == "scenario"
        

        self.scenario_nodes = [
            (node_id, data) for node_id, data in self.graph.nodes(data=True)
            if data.get('type') == 'scenario'
        ]
  
        print(f"Found {len(self.scenario_nodes)} scenario nodes")
        
        # Extract example texts
        scenario_texts = []
        for node_id, data in self.scenario_nodes:
            example_text = data.get('example', '')
            if not example_text:
                # Fallback to node_id if no example text
        
                example_text = str(node_id)
            scenario_texts.append(example_text)
        
        # Compute embeddings
        if scenario_texts:
            self.scenario_embeddings = self.model.encode(scenario_texts)
            print(f"Computed embeddings for {len(scenario_texts)} scenarios")
        else:
            self.scenario_embeddings = np.array([])
            print("Warning: No scenario texts found for embedding")
    
    def find_matching_scenario(self, query: str, threshold: float = 0.65) -> Optional[Tuple[str, float]]:
        """
        Find the closest matching scenario for a given query.
        
        Args:
            query: User query string
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            Tuple of (scenario_id, similarity_score) if match found, None otherwise
        """
        threshold = 0.65
        if not query.strip():
            return None
        
        if len(self.scenario_nodes) == 0 or self.scenario_embeddings.size == 0:
            print("No scenarios available for matching")
            return None
        
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_embedding, self.scenario_embeddings)[0]
        
        # Find the best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        print(f"Best match score: {best_score:.3f} (threshold: {threshold})")
        
        if best_score >= threshold:
            best_scenario_id = self.scenario_nodes[best_idx][0]
            return best_scenario_id, best_score
        
        return None
    
    def get_top_matches(self, query: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Get top K matching scenarios with their similarity scores.
        
        Args:
            query: User query string
            top_k: Number of top matches to return
            
        Returns:
            List of tuples (scenario_id, similarity_score, example_text)
        """
        if not query.strip() or len(self.scenario_nodes) == 0:
            return []
        
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_embedding, self.scenario_embeddings)[0]
        
        # Get top K indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            scenario_id = self.scenario_nodes[idx][0]
            score = similarities[idx]
            example_text = self.scenario_nodes[idx][1].get('example', '')
            results.append((scenario_id, score, example_text))
        
  
        
        return results
    
    def refresh_embeddings(self):
        """Refresh embeddings after graph updates."""
        self._prepare_scenario_embeddings()


# Standalone function for easy LLM code generation
def find_matching_scenario(query: str, threshold: float = 0.65, 
                          graph_path: str = "law_graphTest.gpickle") -> Optional[str]:
    """
    Simple interface function to find matching scenario.
    
    Args:
        query: User query string
        threshold: Minimum similarity threshold
        graph_path: Path to the legal graph
        
    Returns:
        Scenario ID if match found, None otherwise
    """
    matcher = SemanticMatcher(graph_path)
    result = matcher.find_matching_scenario(query, threshold)
    return result[0] if result else None


if __name__ == "__main__":
    # Test the semantic matcher
    try:
        matcher = SemanticMatcher()
        
        # Test queries
        test_queries = [
            "I was arrested during a peaceful protest",
            "My employer fired me without notice",
            "Can police search my house without warrant?",
            "What are my rights during interrogation?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = matcher.find_matching_scenario(query, threshold=0.5)
            if result:
                scenario_id, score = result
                print(f"Match: {scenario_id} (score: {score:.3f})")
                
                # Show the matched scenario details
                scenario_data = matcher.graph.nodes[scenario_id]
                print(f"Example: {scenario_data.get('example', 'N/A')}")
            else:
                print("No match found")
                
                # Show top 3 closest matches
                top_matches = matcher.get_top_matches(query, top_k=3)
                print("Top 3 closest matches:")
                for i, (sid, score, example) in enumerate(top_matches, 1):
                    print(f"  {i}. {sid} (score: {score:.3f})")
                    print(f"     Example: {example[:100]}...")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the law_graphfinal.gpickle file exists and sentence-transformers is installed:")
        print("pip install sentence-transformers scikit-learn")