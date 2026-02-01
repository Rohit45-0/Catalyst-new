from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI
import os
import json
import logging

# Configure logging if not already configured
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all AI agents. Enforces DRY patterns and consistent error handling.
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        """Initialize the agent with Azure OpenAI client."""
        self.client = self._init_openai_client()
        self.model = model_name or os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        self.temperature = temperature
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _init_openai_client(self) -> AzureOpenAI:
        """Single source of truth for OpenAI client initialization."""
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        key = os.getenv("AZURE_OPENAI_KEY")
        
        if not endpoint or not key:
            self.logger.warning("Azure OpenAI credentials missing in environment variables.")
            
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        )
    
    def _call_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> Any:
        """Reusable LLM call with consistent error handling."""
        # IMPORTANT: Azure OpenAI requires the word 'json' in the message when using json_mode
        if json_mode and "json" not in user_prompt.lower():
            user_prompt = f"{user_prompt}\n\nRespond with valid JSON format."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            self.logger.info(f"Calling LLM: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                response_format={"type": "json_object"} if json_mode else None
            )
            content = response.choices[0].message.content
            
            if json_mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse LLM response as JSON")
                    return {"error": "Invalid JSON response", "raw_content": content}
            return content
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            # We don't raise here to allow agent recovery, or we could raise custom exceptions
            return {"error": str(e)}
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main logic.
        Must be implemented by concrete classes.
        """
        pass
