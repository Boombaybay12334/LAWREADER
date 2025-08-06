"""LLM client using Mistral 7B via OpenRouter API."""

import time
from openai import OpenAI
from typing import Optional

from .config import Config
from .exceptions import APIError
from .logger import setup_logger

logger = setup_logger(__name__)

class LLMClient:
    """Client that only uses Mistral 7B from OpenRouter."""

    def __init__(self, config: Config):
        """
        Initialize the Mistral-only LLM client.

        Args:
            config: Configuration object
        """
        self.config = config
        self.model = config.MISTRAL_MODEL or "mistralai/mistral-7b-instruct"

        if not config.OPENROUTER_API_KEY:
            raise APIError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY
        )

        self.extra_headers = {
            "HTTP-Referer": "https://yourproject.com",  # optional
            "X-Title": "LegalDocumentAnalyzer"          # optional
        }

        logger.info("Mistral 7B via OpenRouter initialized")

    def generate_response(self, prompt: str, max_retries: Optional[int] = None) -> str:
        """
        Generate a response using Mistral 7B.

        Args:
            prompt: User input string
            max_retries: Optional number of retries

        Returns:
            LLM response string

        Raises:
            APIError on failure
        """
        max_retries = max_retries or self.config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3,
                    extra_headers=self.extra_headers
                )
                return completion.choices[0].message.content

            except Exception as e:
                logger.warning(f"Mistral API call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise APIError(f"Mistral API failed after {max_retries} attempts: {e}")
