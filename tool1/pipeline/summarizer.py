# File: pipeline/summarizer.py
"""Document summarization module using LLM."""


from .llm_client import LLMClient
from .exceptions import SummarizationError
from .logger import setup_logger

logger = setup_logger(__name__)

class DocumentSummarizer:
    """Summarize legal documents using LLM."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize document summarizer.
        
        Args:
            llm_client: LLM client for generating responses
        """
        self.llm_client = llm_client
    
    def summarize_text(self, text: str, context: str = "") -> str:
        """
        Generate plain-language summary of legal text.
        
        Args:
            text: Text to summarize
            context: Additional context (e.g., document type)
            
        Returns:
            Plain-language summary
            
        Raises:
            SummarizationError: If summarization fails
        """
        try:
            logger.debug(f"Summarizing {len(text)} characters of text")
            
            context_info = f" This is from a {context}." if context else ""
            
            prompt = f"""
            You are an expert legal summarizer. Your task is to create a clear, concise simplifcation of the provided legal text in plain language.
            You will be given a legal text and some context about the document type. Your simplifcation should help a layperson understand the key points and implications of the text,Without missing any points.
            Simplify the following legal text in simple, clear language that a layperson can understand.{context_info}
            
            Guidelines:
            - Use plain English, avoid legal jargon where possible
            - Explain key concepts in simple terms
            - Focus on the main points and outcomes
            - Keep the summary concise but comprehensive
            - If technical legal terms must be used, provide brief explanations
            
            Text to summarize:
            {text}
            
            Summary:
            """
            
            summary = self.llm_client.generate_response(prompt)
            
            logger.debug(f"Generated summary of {len(summary)} characters")
            return summary.strip()
            
        except Exception as e:
            raise SummarizationError(f"Failed to summarize text: {e}")