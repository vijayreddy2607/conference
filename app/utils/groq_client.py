"""Dedicated Groq API client for fast LLM inference."""
import os
import logging
import asyncio
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class GroqClient:
    """Lightweight async Groq API client."""

    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_TIMEOUT = 3.5
    DEFAULT_MAX_TOKENS = 150

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                logger.error("groq package not installed. Run: pip install groq")
                raise
        return self._client

    def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 0.8,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Optional[str]:
        """Synchronous completion."""
        try:
            client = self._get_client()
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            response = client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None

    async def complete_async(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 0.8,
    ) -> Optional[str]:
        """Async completion using thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.complete(messages, system_prompt, max_tokens, temperature)
        )


# Global instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
