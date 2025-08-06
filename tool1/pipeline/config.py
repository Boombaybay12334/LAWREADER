import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # make sure .env is loaded

@dataclass
class Config:
    """Configuration class for the legal document analyzer."""

    # API Keys

    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")

    # Model settings
    CLASSIFICATION_MODEL: str = "facebook/bart-large-mnli"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mistral").lower()
    

    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistralai/mistral-7b-instruct")

    # Processing settings
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", 1000))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 2000))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))

    # Document types
    DOCUMENT_TYPES = [
        "Court Judgment",
        "Contract/Agreement",
        "Statute/Act",
        "Legal Notice",
        "Petition/Writ"
    ]

    # Contract clause types
    CONTRACT_CLAUSES = [
        "Definitions",
        "Confidentiality",
        "Obligations",
        "Payment Terms",
        "Termination",
        "Dispute Resolution",
        "Miscellaneous"
    ]
