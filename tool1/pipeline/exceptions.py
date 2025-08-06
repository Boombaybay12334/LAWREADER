# File: pipeline/exceptions.py
"""Custom exceptions for the legal document analyzer."""

class LegalAnalyzerError(Exception):
    """Base exception for legal document analyzer."""
    pass

class PDFExtractionError(LegalAnalyzerError):
    """Exception raised when PDF text extraction fails."""
    pass

class DocumentTypeDetectionError(LegalAnalyzerError):
    """Exception raised when document type detection fails."""
    pass

class SegmentationError(LegalAnalyzerError):
    """Exception raised when document segmentation fails."""
    pass

class CitationExtractionError(LegalAnalyzerError):
    """Exception raised when citation extraction fails."""
    pass

class SummarizationError(LegalAnalyzerError):
    """Exception raised when summarization fails."""
    pass

class APIError(LegalAnalyzerError):
    """Exception raised when API calls fail."""
    pass

