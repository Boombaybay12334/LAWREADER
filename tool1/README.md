# Legal Document Analyzer Pipeline

A complete, modular, production-grade Python pipeline for AI-powered Indian legal document analysis.

## Features

- **Multi-format Support**: Analyze Court Judgments, Contracts, Statutes, Legal Notices, and Petitions
- **Intelligent Segmentation**: Document-type-specific parsing using LLMs and zero-shot classification
- **Citation Extraction**: AI-powered extraction of legal citations, case names, and statutory references
- **Plain Language Summaries**: Generate layperson-friendly summaries of complex legal text
- **Modular Architecture**: Clean, maintainable code with proper error handling and logging
- **Production Ready**: Comprehensive exception handling, logging, and configuration management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd legal-document-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# For Gemini API
export GOOGLE_API_KEY="your-gemini-api-key"

# For OpenAI API (optional)
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

### Command Line Interface

```bash
# Basic usage
python -m pipeline.main --file document.pdf

# JSON output
python -m pipeline.main --file document.pdf --output json

# Debug logging
python -m pipeline.main --file document.pdf --log-level DEBUG

# Save logs to file
python -m pipeline.main --file document.pdf --log-file analysis.log
```

### Python API

```python
from pipeline.main import LegalDocumentAnalyzer
from pipeline.config import Config

# Initialize analyzer
config = Config()
analyzer = LegalDocumentAnalyzer(config)

# Analyze document
results = analyzer.analyze_document("document.pdf")

# Print results
analyzer.print_results(results)
```

## Architecture

### Core Modules

- **`parser.py`**: PDF text extraction using pdfplumber
- **`type_detector.py`**: Zero-shot document type classification
- **`segmenter.py`**: Document-specific segmentation logic
- **`citation_extractor.py`**: LLM-based citation extraction
- **`summarizer.py`**: Plain-language summarization
- **`main.py`**: CLI interface and orchestration

### Document Processing Pipeline

1. **Text Extraction**: Extract text from PDF using pdfplumber
2. **Type Detection**: Classify document type using zero-shot classification
3. **Segmentation**: Parse document into meaningful sections based on type
4. **Citation Extraction**: Extract legal references using LLM prompts
5. **Summarization**: Generate plain-language summaries for each section

### Document Types & Segmentation

- **Court Judgments**: Facts → Arguments → Decision → Order
- **Contracts**: Paragraph-based with clause classification
- **Statutes/Acts**: Section-based parsing using regex
- **Legal Notices**: Introduction → Claim → Relief Sought
- **Petitions/Writs**: Parties → Grounds → Prayer → Affidavit

## Configuration

The system supports configuration through environment variables and the `Config` class:

```python
# API Configuration
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Model Configuration
LLM_PROVIDER=gemini  # or "openai"
CLASSIFICATION_MODEL=facebook/bart-large-mnli

# Processing Configuration
MAX_TEXT_LENGTH=1000
CHUNK_SIZE=2000
MAX_RETRIES=3
```

## Error Handling

The pipeline includes comprehensive error handling:

- **PDFExtractionError**: PDF parsing failures
- **DocumentTypeDetectionError**: Classification failures
- **SegmentationError**: Document parsing failures
- **CitationExtractionError**: Citation extraction failures
- **SummarizationError**: Summarization failures
- **APIError**: LLM API call failures

## Logging

Structured logging with multiple levels:

```bash
# Set log level
python -m pipeline.main --file doc.pdf --log-level DEBUG

# Save to file
python -m pipeline.main --file doc.pdf --log-file analysis.log
```

## Performance Considerations

- **GPU Support**: Automatic GPU detection for transformer models
- **Batch Processing**: Efficient processing of multiple segments
- **Error Recovery**: Graceful handling of API failures with retries
- **Memory Management**: Chunked processing for large documents

## Legal Document Types

### Supported Formats

1. **Court Judgments**
   - Automatic segmentation into Facts, Arguments, Decision, Order
   - Citation extraction for case references
   - Plain-language summaries of judicial reasoning

2. **Contracts/Agreements**
   - Clause-by-clause analysis
   - Automatic classification of contract provisions
   - Key term extraction and summarization

3. **Statutes/Acts**
   - Section-wise parsing
   - Cross-reference extraction
   - Simplified explanations of legal provisions

4. **Legal Notices**
   - Structured parsing of claims and demands
   - Timeline extraction
   - Summary of legal implications

5. **Petitions/Writs**
   - Party identification
   - Ground-wise analysis
   - Relief sought summarization

## Example Output

```
================================================================================
LEGAL DOCUMENT ANALYSIS RESULTS
================================================================================

File: sample_judgment.pdf
Document Type: Court Judgment
Confidence: 0.945

Processing Summary:
  Text Length: 15,432 characters
  Segments Found: 4
  Total Citations: 12
  Successful Summaries: 4

================================================================================
DOCUMENT SEGMENTS
================================================================================

1. Facts
------------------------------------------------------------
SUMMARY:
The case involves a contract dispute between ABC Corp and XYZ Ltd regarding
the supply of goods worth Rs. 10 lakhs. The plaintiff claims breach of
contract due to delayed delivery and defective goods.

CITATIONS:
  Case Citations:
    • Indian Oil Corp v. Amritsar Gas Service (1991) 1 SCC 533
    • Satyabrata Ghose v. Mugneeram Bangur & Co. AIR 1954 SC 44
  
  Statutory References:
    • Section 73 of the Indian Contract Act, 1872
    • Section 55 of the Sale of Goods Act, 1930
```

## Development

### Testing

```bash
# Run basic tests
python -m pytest tests/

# Test specific modules
python -m pytest tests/test_parser.py
python -m pytest tests/test_segmenter.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the example outputs

## Disclaimer

This tool is designed to assist with legal document analysis but should not be considered a substitute for professional legal advice. Always consult with qualified legal professionals for important legal matters.