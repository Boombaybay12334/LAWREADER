# File: pipeline/citation_extractor.py
"""Citation extraction module using LLM."""

from typing import  List, Dict, Any

from .llm_client import LLMClient
from .exceptions import CitationExtractionError
from .logger import setup_logger

logger = setup_logger(__name__)

class CitationExtractor:
    """Extract legal citations using LLM."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize citation extractor.
        
        Args:
            llm_client: LLM client for generating responses
        """
        self.llm_client = llm_client
    
    def extract_citations(self, text: str) -> Dict[str, Any]:
        """
        Extract citations from text using LLM.
        
        Args:
            text: Text to extract citations from
            
        Returns:
            Dictionary containing extracted citations
            
        Raises:
            CitationExtractionError: If citation extraction fails
        """
        try:
            logger.debug(f"Extracting citations from {len(text)} characters of text")
            
            prompt = f"""
            Extract all legal citations, case names, statutory references, and legal authorities from the following text.
            
            Please identify and list:
            1. Case citations (e.g., "ABC v. XYZ (2023) 1 SCC 123")
            2. Statutory references (e.g., "Section 123 of the Indian Penal Code", "Article 14 of the Constitution")
            3. Legal authorities (e.g., Supreme Court, High Court names)
            4. Act names (e.g., "Companies Act, 2013")
            5. Any other legal references
            
            Text to analyze:
            {text}
            
            Please format your response as a structured list:
            CASE CITATIONS:
            - [citation 1]
            - [citation 2]
            
            STATUTORY REFERENCES:
            - [reference 1]
            - [reference 2]
            
            LEGAL AUTHORITIES:
            - [authority 1]
            - [authority 2]
            
            ACT NAMES:
            - [act 1]
            - [act 2]
            
            OTHER REFERENCES:
            - [reference 1]
            - [reference 2]
            
            If no citations are found in a category, write "None found".
            """
            
            response = self.llm_client.generate_response(prompt)
            parsed_citations = self._parse_citations(response)
            
            logger.info(f"Extracted {sum(len(v) for v in parsed_citations.values())} citations")
            return parsed_citations
            
        except Exception as e:
            raise CitationExtractionError(f"Failed to extract citations: {e}")
    
    def _parse_citations(self, response: str) -> Dict[str, List[str]]:
        """Parse LLM response into structured citations."""
        citations = {
            'case_citations': [],
            'statutory_references': [],
            'legal_authorities': [],
            'act_names': [],
            'other_references': []
        }
        
        current_category = None
        category_map = {
            'CASE CITATIONS:': 'case_citations',
            'STATUTORY REFERENCES:': 'statutory_references',
            'LEGAL AUTHORITIES:': 'legal_authorities',
            'ACT NAMES:': 'act_names',
            'OTHER REFERENCES:': 'other_references'
        }
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if line is a category header
            if line in category_map:
                current_category = category_map[line]
                continue
            
            # Check if line is a citation item
            if line.startswith('- ') and current_category:
                citation = line[2:].strip()
                if citation and citation.lower() != "none found":
                    citations[current_category].append(citation)
        
        return citations