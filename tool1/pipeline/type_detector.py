# File: pipeline/type_detector.py
"""Document type detection using zero-shot classification."""

from transformers import pipeline
from typing import Dict, Any
import torch

from .config import Config
from .exceptions import DocumentTypeDetectionError
from .logger import setup_logger

logger = setup_logger(__name__)

class DocumentTypeDetector:
    """Detect document type using zero-shot classification."""
    
    def __init__(self, config: Config):
        """
        Initialize document type detector.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """Load the zero-shot classification model."""
        try:
            logger.info(f"Loading classification model: {self.config.CLASSIFICATION_MODEL}")
            
            device = 0 if torch.cuda.is_available() else -1
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.config.CLASSIFICATION_MODEL,
                device=device
            )
            
            logger.info("Classification model loaded successfully")
            
        except Exception as e:
            raise DocumentTypeDetectionError(f"Failed to load classification model: {e}")
    
    def detect_type(self, text: str) -> Dict[str, Any]:
        """
        Detect document type from text.
        
        Args:
            text: Document text (first 500-1000 characters recommended)
            
        Returns:
            Dictionary with detected type and confidence scores
            
        Raises:
            DocumentTypeDetectionError: If type detection fails
        """
        try:
            # Truncate text for classification
            text_sample = text[:self.config.MAX_TEXT_LENGTH].strip()
            
            if not text_sample:
                raise DocumentTypeDetectionError("Empty text provided for classification")
            
            logger.info("Detecting document type...")
            logger.debug(f"Classifying text sample of {len(text_sample)} characters")
            
            # Perform zero-shot classification
            result = self.classifier(text_sample, self.config.DOCUMENT_TYPES)
            
            detected_type = result['labels'][0]
            confidence = result['scores'][0]
            
            logger.info(f"Detected document type: {detected_type} (confidence: {confidence:.3f})")
            
            return {
                'type': detected_type,
                'confidence': confidence,
                'all_scores': dict(zip(result['labels'], result['scores']))
            }
            
        except Exception as e:
            if isinstance(e, DocumentTypeDetectionError):
                raise
            raise DocumentTypeDetectionError(f"Failed to detect document type: {e}")