# File: pipeline/parser.py
"""PDF text extraction module."""

import pdfplumber

from pathlib import Path

from .exceptions import PDFExtractionError
from .logger import setup_logger

logger = setup_logger(__name__)

class PDFParser:
    """Extract text from PDF files using pdfplumber."""
    
    def __init__(self):
        """Initialize PDF parser."""
        logger.info("Initializing PDF parser")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            PDFExtractionError: If text extraction fails
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise PDFExtractionError(f"File not found: {file_path}")
            
            if not file_path.suffix.lower() == '.pdf':
                raise PDFExtractionError(f"File is not a PDF: {file_path}")
            
            logger.info(f"Extracting text from: {file_path}")
            
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"PDF has {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                            logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
                        else:
                            logger.warning(f"No text found on page {page_num}")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        continue
            
            if not text_content:
                raise PDFExtractionError("No text could be extracted from the PDF")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            if isinstance(e, PDFExtractionError):
                raise
            raise PDFExtractionError(f"Failed to extract text from PDF: {e}")