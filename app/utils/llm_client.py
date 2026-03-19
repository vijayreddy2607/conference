"""LLM client with support for Ollama (local free models)."""
from typing import List
from langchain_core.messages import BaseMessage, AIMessage
from app.config import settings
import logging
import httpx

logger = logging.getLogger(__name__)


class OllamaLLMClient:
    """Client for Ollama local LLM."""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ollama_base_url', 'http://localhost:11434')
        self.model = getattr(settings, 'ollama_model', 'llama3.1:8b')
        logger.info(f"Initialized Ollama client: {self.model} at {self.base_url}")
    
    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        """
        Invoke Ollama API asynchronously.
        
        Args:
            messages: List of LangChain messages
            
        Returns:
            Generated text response
        """
        try:
            # Convert LangChain messages to Ollama format
            prompt = self._format_messages(messages)
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
                result = response.json()
                return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Ollama invocation failed: {e}")
            raise
    
    def _format_messages(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt for Ollama."""
        prompt_parts = []
        
        for msg in messages:
            role = msg.__class__.__name__
            content = msg.content
            
            if "SystemMessage" in role:
                prompt_parts.append(f"System: {content}\n")
            elif "HumanMessage" in role:
                prompt_parts.append(f"User: {content}\n")
            elif "AIMessage" in role:
                prompt_parts.append(f"Assistant: {content}\n")
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)


class LLMClient:
    """Universal LLM client supporting multiple providers."""
    
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        logger.info(f"Initializing LLM client with provider: {self.provider}")
        
        if self.provider == "ollama":
            self.client = OllamaLLMClient()
        elif self.provider == "openai":
            from langchain_openai import ChatOpenAI
            self.client = ChatOpenAI(
                model=settings.openai_model,
                temperature=0.7
            )
        elif self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self.client = ChatAnthropic(
                model=settings.anthropic_model,
                temperature=0.7
            )
        elif self.provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.client = ChatGoogleGenerativeAI(
                model=settings.google_model,
                temperature=0.7
            )
        elif self.provider == "groq":
            # Groq uses OpenAI-compatible API (fast & free!)
            from langchain_openai import ChatOpenAI
            self.client = ChatOpenAI(
                model=settings.groq_model,
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url,
                temperature=0.7
            )
            logger.info(f"⚡ Groq initialized: {settings.groq_model}")
        elif self.provider == "grok":
            # Grok uses OpenAI-compatible API
            from langchain_openai import ChatOpenAI
            self.client = ChatOpenAI(
                model=settings.grok_model,
                api_key=settings.grok_api_key,
                base_url=settings.grok_base_url,
                temperature=0.7
            )
            logger.info(f"✨ Grok initialized: {settings.grok_model}")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        """
        Invoke LLM asynchronously.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Generated response text
        """
        try:
            if self.provider == "ollama":
                return await self.client.ainvoke(messages)
            else:
                # For LangChain providers
                response = await self.client.ainvoke(messages)
                return response.content
        
        except Exception as e:
            logger.error(f"Async LLM invocation failed: {e}")
            raise


# Global client instance
llm_client = LLMClient()
