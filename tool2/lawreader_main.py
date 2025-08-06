# lawreader_main.py
#!/usr/bin/env python3
"""
LAWREADER Tool 2 - Main Orchestrator

A code-generatable legal AI tool for Indian law that:
* Uses a prebuilt legal graph (law_graphfinal.gpickle)
* Resolves legal queries using the graph
* Falls back to LLM only if no graph match
* Updates the graph with new LLM-generated nodes when needed
"""

import sys
import os
import argparse
from typing import Dict, Any, Optional
import time

# Import our modules
from semantic_matcher import SemanticMatcher, find_matching_scenario
from traversal import GraphTraversal, expand_context
from answer_simplifier import AnswerSimplifier, simplify_answer
from auto_linker import AutoLinker
from dotenv import load_dotenv
load_dotenv()
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')




class LawReader:
    def __init__(self, graph_path: str,
                 similarity_threshold: float = 0.75,
                 llm_api_key: Optional[str] = None,
                 llm_endpoint: Optional[str] = None):
        """
        Initialize the LawReader system.
        
        Args:
            graph_path: Path to the legal graph pickle file
            similarity_threshold: Minimum similarity for scenario matching
            llm_api_key: API key for LLM service
            llm_endpoint: Endpoint URL for LLM service
        """
        self.graph_path = "law_graphTest.gpickle"
        self.similarity_threshold = similarity_threshold
        
        # Initialize components
        print("Initializing LawReader components...")
        try:
            self.matcher = SemanticMatcher(graph_path)
            self.traversal = GraphTraversal(graph_path)
            self.simplifier = AnswerSimplifier()
            self.auto_linker = AutoLinker(graph_path, llm_api_key, llm_endpoint)
            print("All components initialized successfully")
        except Exception as e:
            print(f"Failed to initialize components: {e}")
            raise
    
    def process_query(self, query: str, force_llm: bool = False) -> Dict[str, Any]:
        """
        Process a legal query through the complete pipeline.
        
        Args:
            query: User's legal query
            force_llm: If True, skip graph matching and use LLM directly
            
        Returns:
            Dictionary with processing results and answer
        """
        start_time = time.time()
        
        result = {
            'query': query,
            'processing_time': 0,
            'method_used': '',
            'success': False,
            'answer': '',
            'context': {},
            'debug_info': {}
        }
        
        try:
            if not force_llm:
                # Step 1: Try to match scenario in existing graph
                print(f" Searching for matching scenario (threshold: {self.similarity_threshold})")
                match_result = self.matcher.find_matching_scenario(query, self.similarity_threshold)
                
                if match_result:
                    scenario_id, similarity_score = match_result
                    print(f"Found matching scenario: {scenario_id} (score: {similarity_score:.3f})")
                    
                    # Step 2: Expand context from matched scenario
                    print("Expanding legal context...")
                    context = self.traversal.expand_context(scenario_id)
                    
                    # Step 3: Simplify answer
                    print(" Generating simplified answer...")
                    answer = self.simplifier.simplify_answer(context)
                    
                    result.update({
                        'method_used': 'graph_match',
                        'success': True,
                        'answer': answer,
                        'context': context,
                        'debug_info': {
                            'matched_scenario_id': scenario_id,
                            'similarity_score': similarity_score,
                            'principles_found': len(context.get('principles', [])),
                            'articles_found': len(context.get('articles', []))
                        }
                    })
                    
                else:
                    print(f" No matching scenario found (best score below {self.similarity_threshold})")
                    # Show top matches for debugging
                    top_matches = self.matcher.get_top_matches(query, top_k=3)
                    if top_matches:
                        print("Top 3 closest matches:")
                        for i, (sid, score, example) in enumerate(top_matches, 1):
                            print(f"  {i}. {sid} (score: {score:.3f})")
                            print(f"     Example: {example}...")
                    
                    force_llm = True  # Fall back to LLM
            
            if force_llm:
                # Step 4: Use LLM to generate new legal context
                print(" Using LLM to generate new legal context...")
                llm_result = self.auto_linker.generate_and_insert(query)
                if llm_result['success']:
                    print(" LLM successfully generated new legal context")

                    # 🔄 Update in-memory graphs across components
                    updated_graph = self.auto_linker.graph
                    self.matcher.graph = updated_graph
                    self.traversal.graph = updated_graph

                    # Save the graph to disk before any reloads (expand_context, etc.)
                    self.auto_linker._save_graph()
                    # Refresh matcher embeddings to include new scenario
                    print(" Refreshing semantic matcher with new scenarios...")
                    self.matcher.refresh_embeddings()

                    new_scenario_id = llm_result.get("scenario")
                    context = self.traversal.expand_context(new_scenario_id)
                    # Step 5: Simplify the LLM-generated answer
                    print("Generating simplified answer from LLM context...")
                    answer = self.simplifier.simplify_answer(context)

                    result.update({
                        'method_used': 'llm_generation',
                        'success': True,
                        'answer': answer,
                        'context': context,
                        'debug_info': {
                            'nodes_created': llm_result['nodes_created'],
                            'llm_response': llm_result.get('llm_response'),
                            'new_scenario_id': new_scenario_id
                        }
                    })
                else:
                    print(f"LLM generation failed: {llm_result.get('error')}")
                    result.update({
                        'method_used': 'llm_generation',
                        'success': False,
                        'answer': f"Unable to process your legal query. Error: {llm_result.get('error')}",
                        'debug_info': {'llm_error': llm_result.get('error')}
                    })
        
        except Exception as e:
            print(f"Error processing query: {e}")
            result.update({
                'success': False,
                'answer': f"System error while processing your query: {str(e)}",
                'debug_info': {'system_error': str(e)}
            })
        
        finally:
            result['processing_time'] = round(time.time() - start_time, 2)
            print(f" Total processing time: {result['processing_time']}s")
        
        return result
    
    def interactive_mode(self):
        """Run the LawReader in interactive mode."""
        print("LAWREADER Tool 2 - Interactive Mode")
        print("=" * 50)
        print("Ask legal questions about Indian law.")
        print("Type 'quit', 'exit', or 'q' to stop.")
        print("Type 'debug' to toggle debug information.")
        print("Type 'stats' to see graph statistics.")
        print("=" * 50)
        
        show_debug = False
        
        while True:
            try:
                query = input("\n Legal Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print(" Goodbye!")
                    break
                
                if query.lower() == 'debug':
                    show_debug = not show_debug
                    print(f" Debug mode: {'ON' if show_debug else 'OFF'}")
                    continue
                
                if query.lower() == 'stats':
                    self._show_stats()
                    continue
                
                if not query:
                    continue
                
                print("\n" + "=" * 50)
                result = self.process_query(query)
                
                print("\n ANSWER:")
                print(result['answer'])
                
                if show_debug:
                    print(f"\n DEBUG INFO:")
                    print(f"   Method: {result['method_used']}")
                    print(f"   Success: {result['success']}")
                    print(f"   Time: {result['processing_time']}s")
                    if result['debug_info']:
                        for key, value in result['debug_info'].items():
                            print(f"   {key}: {value}")
                
            except KeyboardInterrupt:
                print("\n Goodbye!")
                break
            except Exception as e:
                print(f"\n Error: {e}")
    
    def _show_stats(self):
        """Show graph statistics."""
        graph = self.matcher.graph
        
        # Count nodes by type
        node_types = {}
        auto_generated = 0
        for node_id, data in graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
            if data.get('auto_generated', False):
                auto_generated += 1
        
        # Count edges by type
        edge_types = {}
        for u, v, data in graph.edges(data=True):
            edge_type = data.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        print("\n GRAPH STATISTICS:")
        print(f"   Total Nodes: {graph.number_of_nodes()}")
        print(f"   Total Edges: {graph.number_of_edges()}")
        print(f"   Auto-generated Nodes: {auto_generated}")
        
        print("\n   Node Types:")
        for node_type, count in sorted(node_types.items()):
            print(f"     {node_type}: {count}")
        
        print("\n   Edge Types:")
        for edge_type, count in sorted(edge_types.items()):
            print(f"     {edge_type}: {count}")


def main():
    """Main entry point for the LawReader tool."""
    parser = argparse.ArgumentParser(
        description=" LAWREADER Tool 2 - Legal AI for Indian Law",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lawreader_main.py                                    # Interactive mode
  python lawreader_main.py -q "Can police arrest without warrant?"  # Single query
  python lawreader_main.py --threshold 0.6                   # Lower similarity threshold
  python lawreader_main.py --force-llm -q "New legal query"  # Force LLM usage
        """
    )
    
    parser.add_argument('-q', '--query', 
                       help='Single legal query to process')
    parser.add_argument('--graph-path', default='law_graphTest.gpickle',
                       help='Path to the legal graph file')
    parser.add_argument('--threshold', type=float, default=0.75,
                       help='Similarity threshold for scenario matching (0.0-1.0)')
    parser.add_argument('--force-llm', action='store_true',
                       help='Skip graph matching and use LLM directly')
    parser.add_argument('--llm-endpoint',
                       help='LLM API endpoint URL')
    parser.add_argument('--llm-api-key',
                       help='LLM API key')
    parser.add_argument('--debug', action='store_true',
                       help='Show debug information')
    
    args = parser.parse_args()
    
    try:
        # Initialize LawReader
        lawreader = LawReader(
            graph_path="law_graphTest.gpickle",
            similarity_threshold=args.threshold,
            llm_api_key=os.getenv("LLM_API_KEY") or args.llm_api_key,
            llm_endpoint=args.llm_endpoint
        )
        
        if args.query:
            # Process single query
            result = lawreader.process_query(args.query, force_llm=args.force_llm)
            
            print("\n ANSWER:")
            print(result['answer'])
            




            if args.debug:
                print(f"\n DEBUG INFO:")
                print(f"   Method: {result['method_used']}")
                print(f"   Success: {result['success']}")
                print(f"   Time: {result['processing_time']}s")
                if result['debug_info']:
                    for key, value in result['debug_info'].items():
                        print(f"   {key}: {value}")
        else:
            # Interactive mode
            lawreader.interactive_mode()
    
    except FileNotFoundError as e:

        print(f" Graph file not found: {e}")
        print("Make sure 'law_graphfinal.gpickle' exists in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f" Failed to initialize LawReader: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()