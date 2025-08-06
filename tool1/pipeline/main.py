# File: pipeline/main.py
"""Main CLI module for the legal document analyzer."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from fpdf import FPDF

from dotenv import load_dotenv
load_dotenv()

from .config import Config


from .config import Config
from .parser import PDFParser
from .type_detector import DocumentTypeDetector
from .segmenter import DocumentSegmenter
from .citation_extractor import CitationExtractor
from .summarizer import DocumentSummarizer
from .llm_client import LLMClient
from .exceptions import LegalAnalyzerError
from .logger import setup_logger

logger = setup_logger(__name__)

class LegalDocumentAnalyzer:
    """Main analyzer class that orchestrates the entire pipeline."""
    
    def __init__(self, config: Config = None):
        """
        Initialize the legal document analyzer.
        
        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        
        # Initialize components
        self.pdf_parser = PDFParser()
        self.type_detector = DocumentTypeDetector(self.config)
        self.llm_client = LLMClient(self.config)
        self.segmenter = DocumentSegmenter(self.config, self.llm_client)
        self.citation_extractor = CitationExtractor(self.llm_client)
        self.summarizer = DocumentSummarizer(self.llm_client)
        
        logger.info("Legal document analyzer initialized")
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a legal document through the complete pipeline.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Complete analysis results
            
        Raises:
            LegalAnalyzerError: If analysis fails
        """
        try:
            logger.info(f"Starting analysis of: {file_path}")
            
            # Step 1: Extract text from PDF
            logger.info("Step 1: Extracting text from PDF...")
            raw_text = self.pdf_parser.extract_text(file_path)
            
            # Step 2: Detect document type
            logger.info("Step 2: Detecting document type...")
            type_result = self.type_detector.detect_type(raw_text)
            doc_type = type_result['type']
            
            # Step 3: Segment document
            logger.info("Step 3: Segmenting document...")
            segments = self.segmenter.segment_document(raw_text, doc_type)
            
            # Step 4: Extract citations and summarize each segment
            logger.info("Step 4: Processing segments...")
            processed_segments = []
            
            for segment in segments:
                logger.info(f"Processing segment: {segment['label']}")
                
                # Extract citations
                try:
                    citations = self.citation_extractor.extract_citations(segment['content'])
                except Exception as e:
                    logger.warning(f"Citation extraction failed for segment {segment['label']}: {e}")
                    citations = {}
                
                # Generate summary
                try:
                    summary = self.summarizer.summarize_text(
                        segment['content'], 
                        context=f"{doc_type} - {segment['label']}"
                    )
                except Exception as e:
                    logger.warning(f"Summarization failed for segment {segment['label']}: {e}")
                    summary = "Summary could not be generated."
                
                processed_segments.append({
                    'label': segment['label'],
                    'content': segment['content'],
                    'summary': summary,
                    'citations': citations,
                    **{k: v for k, v in segment.items() if k not in ['label', 'content']}
                })
            
            # Compile final results
            results = {
                'file_path': str(file_path),
                'document_type': {
                    'detected_type': doc_type,
                    'confidence': type_result['confidence'],
                    'all_scores': type_result['all_scores']
                },
                'segments': processed_segments,
                'total_segments': len(processed_segments),
                'total_citations': sum(
                    sum(len(citations) for citations in segment['citations'].values()) 
                    for segment in processed_segments
                ),
                'processing_summary': {
                    'text_length': len(raw_text),
                    'segments_processed': len(processed_segments),
                    'successful_summaries': sum(1 for s in processed_segments if s['summary'] != "Summary could not be generated."),
                    'successful_citations': sum(1 for s in processed_segments if s['citations'])
                }
            }
            
            logger.info(f"Analysis completed successfully. Found {len(processed_segments)} segments.")
            return results
            
        except Exception as e:
            if isinstance(e, LegalAnalyzerError):
                raise
            raise LegalAnalyzerError(f"Document analysis failed: {e}")
    
    def print_results(self, results: Dict[str, Any], output_format: str = "text"):
        """
        Print analysis results in specified format.
        
        Args:
            results: Analysis results dictionary
            output_format: Output format ("text" or "json")
        """
        if output_format.lower() == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return
        
        # Text format output
        print("=" * 80)
        print("LEGAL DOCUMENT ANALYSIS RESULTS")
        print("=" * 80)
        
        print(f"\nFile: {results['file_path']}")
        print(f"Document Type: {results['document_type']['detected_type']}")
        print(f"Confidence: {results['document_type']['confidence']:.3f}")
        
        print(f"\nProcessing Summary:")
        print(f"  Text Length: {results['processing_summary']['text_length']:,} characters")
        print(f"  Segments Found: {results['total_segments']}")
        print(f"  Total Citations: {results['total_citations']}")
        print(f"  Successful Summaries: {results['processing_summary']['successful_summaries']}")
        
        print(f"\n" + "=" * 80)
        print("DOCUMENT SEGMENTS")
        print("=" * 80)
        
        for i, segment in enumerate(results['segments'], 1):
            print(f"\n{i}. {segment['label']}")
            print("-" * 60)
            
            # Print summary
            print("SUMMARY:")
            print(segment['summary'])
            
            # Print citations if any
            if segment['citations']:
                print("\nCITATIONS:")
                for category, citations in segment['citations'].items():
                    if citations:
                        print(f"  {category.replace('_', ' ').title()}:")
                        for citation in citations:
                            print(f"    • {citation}")
            
            # Print additional metadata
            if 'confidence' in segment:
                print(f"\nClassification Confidence: {segment['confidence']:.3f}")
            if 'section_number' in segment and segment['section_number']:
                print(f"Section Number: {segment['section_number']}")
            if 'paragraph_number' in segment:
                print(f"Paragraph Number: {segment['paragraph_number']}")
            
            print()
    

    def make_pdf(self, results: Dict[str, Any], output_file: str = "Legal_Analysis_Report.pdf"):
        """
        Generate a PDF report for the analysis results.

        Args:
            results: Analysis results dictionary
            output_file: PDF file name (default: Legal_Analysis_Report.pdf)
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.add_font('DejaVu', '', r'C:\Users\Atharva\OneDrive\Desktop\legal-document-analyzer\DejaVuLGCSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 14)


        # Title
        pdf.cell(0, 10, "LEGAL DOCUMENT ANALYSIS RESULTS", ln=True, align="C")
        pdf.ln(10)

        # Basic Info
        pdf.set_font("DejaVu", '', 12)
        pdf.cell(0, 10, f"File: {results['file_path']}", ln=True)
        pdf.cell(0, 10, f"Document Type: {results['document_type']['detected_type']}", ln=True)
        pdf.cell(0, 10, f"Confidence: {results['document_type']['confidence']:.3f}", ln=True)

        pdf.ln(5)
        pdf.set_font("DejaVu", '', 12)
        pdf.cell(0, 10, "Processing Summary:", ln=True)

        pdf.set_font("DejaVu", '', 12)
        pdf.cell(0, 10, f"Text Length: {results['processing_summary']['text_length']:,} characters", ln=True)
        pdf.cell(0, 10, f"Segments Found: {results['total_segments']}", ln=True)
        pdf.cell(0, 10, f"Total Citations: {results['total_citations']}", ln=True)
        pdf.cell(0, 10, f"Successful Summaries: {results['processing_summary']['successful_summaries']}", ln=True)

        pdf.ln(10)
        pdf.set_font("DejaVu", '', 12)
        pdf.cell(0, 10, "DOCUMENT SEGMENTS", ln=True)
        pdf.set_font("DejaVu", '', 12)

        for i, segment in enumerate(results['segments'], 1):
            pdf.ln(5)
            pdf.set_font("DejaVu", '', 12)
            pdf.cell(0, 10, f"{i}. {segment['label']}", ln=True)
            pdf.set_font("DejaVu", '', 12)

            # Summary
            pdf.multi_cell(0, 10, f"SUMMARY:\n{segment['summary']}")

            # Citations
            if segment['citations']:
                pdf.multi_cell(0, 10, "CITATIONS:")
                for category, citations in segment['citations'].items():
                    if citations:
                        pdf.multi_cell(0, 10, f"  {category.replace('_', ' ').title()}:")
                        for citation in citations:
                            pdf.multi_cell(0, 10, f"    • {citation}")

            # Additional metadata
            if 'confidence' in segment:
                pdf.cell(0, 10, f"Classification Confidence: {segment['confidence']:.3f}", ln=True)
            if 'section_number' in segment and segment['section_number']:
                pdf.cell(0, 10, f"Section Number: {segment['section_number']}", ln=True)
            if 'paragraph_number' in segment:
                pdf.cell(0, 10, f"Paragraph Number: {segment['paragraph_number']}", ln=True)

        # Save PDF
        pdf.output(output_file)
        logger.info(f"PDF report saved as: {output_file}")



def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="AI-powered Indian Legal Document Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pipeline.main --file judgment.pdf
  python -m pipeline.main --file contract.pdf --output json
  python -m pipeline.main --file act.pdf --log-level DEBUG
        """
    )
    
    parser.add_argument(
        "--file", 
        required=True,
        help="Path to PDF file to analyze"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Path to log file (optional)"
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file (optional)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger("pipeline", args.log_level, args.log_file)
    
    try:
        # Load configuration
        config = Config()
        if args.config:
            # Here you could load custom config from file
            logger.info(f"Loading configuration from: {args.config}")
        
        # Check if file exists
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        
        # Initialize analyzer
        analyzer = LegalDocumentAnalyzer(config)
        
        # Analyze document
        results = analyzer.analyze_document(str(file_path))
        
        # Print results
        analyzer.print_results(results, args.output)
        analyzer.make_pdf(results, output_file="Legal_Analysis_Report.pdf")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except LegalAnalyzerError as e:
        logger.error(f"Analysis error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
