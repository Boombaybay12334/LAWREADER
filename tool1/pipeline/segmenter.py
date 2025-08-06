# File: pipeline/segmenter.py
"""Document segmentation module for different legal document types."""

import re
from typing import List, Dict, Any
from transformers import pipeline
import torch

from .config import Config
from .llm_client import LLMClient
from .exceptions import SegmentationError
from .logger import setup_logger

logger = setup_logger(__name__)

class DocumentSegmenter:
    """Segment documents based on their type using various strategies."""
    
    def __init__(self, config: Config, llm_client: LLMClient):
        """
        Initialize document segmenter.
        
        Args:
            config: Configuration object
            llm_client: LLM client for generating responses
        """
        self.config = config
        self.llm_client = llm_client
        self.clause_classifier = None
        self._load_clause_classifier()
    
    def _load_clause_classifier(self):
        """Load zero-shot classifier for contract clauses."""
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.clause_classifier = pipeline(
                "zero-shot-classification",
                model=self.config.CLASSIFICATION_MODEL,
                device=device
            )
            logger.info("Clause classifier loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load clause classifier: {e}")
    
    def segment_document(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
        """
        Segment document based on its type.
        
        Args:
            text: Full document text
            doc_type: Document type
            
        Returns:
            List of segments with labels and content
            
        Raises:
            SegmentationError: If segmentation fails
        """
        try:
            logger.info(f"Segmenting document of type: {doc_type}")
            
            if doc_type == "Court Judgment":
                return self._segment_judgment(text)
            elif doc_type == "Contract/Agreement":
                return self._segment_contract(text)
            elif doc_type == "Statute/Act":
                return self._segment_act(text)
            elif doc_type == "Legal Notice":
                return self._segment_notice(text)
            elif doc_type == "Petition/Writ":
                return self._segment_petition(text)
            else:
                raise SegmentationError(f"Unknown document type: {doc_type}")
                
        except Exception as e:
            if isinstance(e, SegmentationError):
                raise
            raise SegmentationError(f"Failed to segment document: {e}")
    
    def _segment_judgment(self, text: str) -> List[Dict[str, Any]]:
        """Segment court judgment using LLM."""
        prompt = f"""
        Please analyze the following court judgment and segment it into the following sections:
        1. Facts - The factual background and circumstances of the case
        2. Arguments - The legal arguments presented by parties
        3. Decision - The court's reasoning and legal analysis
        4. Order - The final order or judgment given by the court
        
        For each section, provide the relevant text content. If a section is not present, indicate "Not found".
        
        Text to analyze:
        {text[:self.config.CHUNK_SIZE]}
        
        Please format your response as:
        FACTS:
        [content]
        
        ARGUMENTS:
        [content]
        
        DECISION:
        [content]
        
        ORDER:
        [content]
        """
        
        response = self.llm_client.generate_response(prompt)
        return self._parse_llm_segments(response, ["Facts", "Arguments", "Decision", "Order"])
    
    def _segment_contract(self, text: str) -> List[Dict[str, Any]]:
        """Segment contract using paragraph splitting and clause classification."""
        # Split by double newlines
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        segments = []
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) < 50:  # Skip very short paragraphs
                continue
                
            # Classify paragraph
            if self.clause_classifier:
                try:
                    result = self.clause_classifier(paragraph, self.config.CONTRACT_CLAUSES)
                    clause_type = result['labels'][0]
                    confidence = result['scores'][0]
                except Exception as e:
                    logger.warning(f"Failed to classify paragraph {i}: {e}")
                    clause_type = "Miscellaneous"
                    confidence = 0.0
            else:
                clause_type = "Miscellaneous"
                confidence = 0.0
            
            segments.append({
                'label': clause_type,
                'content': paragraph,
                'confidence': confidence,
                'paragraph_number': i + 1
            })
        
        return segments
    
    def _segment_act(self, text: str) -> List[Dict[str, Any]]:
        """Segment statute/act using regex for sections."""
        # Use regex to find sections (only place regex is allowed as specified)
        section_pattern = r'Section\s+(\d+)'
        
        sections = []
        section_matches = list(re.finditer(section_pattern, text, re.IGNORECASE))
        
        if not section_matches:
            # If no sections found, return entire text as one segment
            return [{
                'label': 'Full Text',
                'content': text,
                'section_number': None
            }]
        
        for i, match in enumerate(section_matches):
            section_num = match.group(1)
            start_pos = match.start()
            
            # Find end position (start of next section or end of text)
            if i + 1 < len(section_matches):
                end_pos = section_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            section_content = text[start_pos:end_pos].strip()
            
            sections.append({
                'label': f'Section {section_num}',
                'content': section_content,
                'section_number': int(section_num)
            })
        
        return sections
    
    def _segment_notice(self, text: str) -> List[Dict[str, Any]]:
        """Segment legal notice using LLM."""
        prompt = f"""
        Please analyze the following legal notice and segment it into these sections:
        1. Introduction - Opening statements and context
        2. Claim - The main claim or complaint being made
        3. Relief Sought - What remedy or action is being demanded
        
        For each section, provide the relevant text content. If a section is not present, indicate "Not found".
        
        Text to analyze:
        {text[:self.config.CHUNK_SIZE]}
        
        Please format your response as:
        INTRODUCTION:
        [content]
        
        CLAIM:
        [content]
        
        RELIEF SOUGHT:
        [content]
        """
        
        response = self.llm_client.generate_response(prompt)
        return self._parse_llm_segments(response, ["Introduction", "Claim", "Relief Sought"])
    
    def _segment_petition(self, text: str) -> List[Dict[str, Any]]:
        """Segment petition/writ using LLM."""
        prompt = f"""
        Please analyze the following petition/writ and segment it into these sections:
        1. Parties - Information about petitioner(s) and respondent(s)
        2. Grounds - The legal grounds and basis for the petition
        3. Prayer - The relief or remedy sought from the court
        4. Affidavit - Any sworn statements or affidavits
        
        For each section, provide the relevant text content. If a section is not present, indicate "Not found".
        
        Text to analyze:
        {text[:self.config.CHUNK_SIZE]}
        
        Please format your response as:
        PARTIES:
        [content]
        
        GROUNDS:
        [content]
        
        PRAYER:
        [content]
        
        AFFIDAVIT:
        [content]
        """
        
        response = self.llm_client.generate_response(prompt)
        return self._parse_llm_segments(response, ["Parties", "Grounds", "Prayer", "Affidavit"])
    
    def _parse_llm_segments(self, response: str, expected_labels: List[str]) -> List[Dict[str, Any]]:
        """Parse LLM response into segments."""
        segments = []
        current_label = None
        current_content = []
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if line is a label
            is_label = False
            for label in expected_labels:
                if line.upper().startswith(label.upper().replace(' ', '').replace('_', '') + ':'):
                    # Save previous segment
                    if current_label and current_content:
                        content = '\n'.join(current_content).strip()
                        if content and content.lower() != "not found":
                            segments.append({
                                'label': current_label,
                                'content': content
                            })
                    
                    # Start new segment
                    current_label = label
                    current_content = []
                    is_label = True
                    break
            
            if not is_label and current_label:
                current_content.append(line)
        
        # Add final segment
        if current_label and current_content:
            content = '\n'.join(current_content).strip()
            if content and content.lower() != "not found":
                segments.append({
                    'label': current_label,
                    'content': content
                })
        
        return segments