"""
LLM Service for communicating with different LLM providers.

This module provides a unified interface for communicating with various
LLM services like Ollama, LM Studio, and other OpenAI-compatible APIs.
"""

import httpx
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..utils.config import get_llm_service_url, get_settings

# Configure logging
logger = logging.getLogger(__name__)


class LLMRequest(BaseModel):
    """Model for LLM request parameters."""
    prompt: str = Field(..., description="The input prompt")
    model: Optional[str] = Field(None, description="Model name to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Maximum tokens to generate")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    stream: bool = Field(False, description="Whether to stream the response")


class LLMResponse(BaseModel):
    """Model for LLM response data."""
    content: str = Field(..., description="Generated response content")
    model_used: str = Field(..., description="Model that generated the response")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")


class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""
    pass


class LLMService:
    """
    Service class for communicating with LLM providers.
    
    This class provides a unified interface for different LLM services,
    handling the specific API requirements for each provider.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=60.0)
        self._service_configs = {
            "ollama": {
                "base_url": self.settings.ollama_base_url,
                "api_path": "/api/generate",
                "headers": {"Content-Type": "application/json"},
            },
            "lm_studio": {
                "base_url": self.settings.lm_studio_base_url,
                "api_path": "/chat/completions",
                "headers": {"Content-Type": "application/json"},
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def generate_response(
        self, 
        request: LLMRequest, 
        service_name: str = "ollama"
    ) -> LLMResponse:
        """
        Generate a response from the specified LLM service.
        
        Args:
            request: LLM request parameters
            service_name: Name of the LLM service to use
            
        Returns:
            LLMResponse: Generated response with metadata
            
        Raises:
            LLMServiceError: If the service is unavailable or returns an error
        """
        start_time = time.time()
        
        try:
            if service_name == "ollama":
                response = await self._call_ollama(request)
            elif service_name == "lm_studio":
                response = await self._call_lm_studio(request)
            else:
                raise LLMServiceError(f"Unsupported service: {service_name}")
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                content=response["content"],
                model_used=response.get("model", "unknown"),
                response_time_ms=response_time_ms,
                tokens_used=response.get("tokens_used"),
                finish_reason=response.get("finish_reason")
            )
            
        except Exception as e:
            logger.error(f"Error generating response from {service_name}: {e}")
            raise LLMServiceError(f"Failed to generate response: {str(e)}")
    
    async def _call_ollama(self, request: LLMRequest) -> Dict[str, Any]:
        """Call Ollama API."""
        config = self._service_configs["ollama"]
        
        payload = {
            "model": request.model or "llama2",
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
        
        url = f"{config['base_url']}{config['api_path']}"
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers=config["headers"]
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "content": data.get("response", ""),
                "model": data.get("model", request.model or "llama2"),
                "tokens_used": None,  # Ollama doesn't provide token count
                "finish_reason": "stop"
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            raise LLMServiceError(f"Ollama API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Ollama request error: {e}")
            raise LLMServiceError(f"Failed to connect to Ollama: {str(e)}")
    
    async def _call_lm_studio(self, request: LLMRequest) -> Dict[str, Any]:
        """Call LM Studio API (OpenAI-compatible)."""
        config = self._service_configs["lm_studio"]
        
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": request.model or "local-model",
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream,
        }
        
        url = f"{config['base_url']}{config['api_path']}"
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers=config["headers"]
            )
            response.raise_for_status()
            
            data = response.json()
            choice = data["choices"][0]
            
            return {
                "content": choice["message"]["content"],
                "model": data.get("model", request.model or "local-model"),
                "tokens_used": data.get("usage", {}).get("total_tokens"),
                "finish_reason": choice.get("finish_reason", "stop")
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"LM Studio API error: {e.response.status_code} - {e.response.text}")
            raise LLMServiceError(f"LM Studio API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"LM Studio request error: {e}")
            raise LLMServiceError(f"Failed to connect to LM Studio: {str(e)}")
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Check the health status of an LLM service.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            Dict containing health status information
        """
        start_time = time.time()
        
        try:
            config = self._service_configs.get(service_name)
            if not config:
                return {
                    "status": "error",
                    "error": f"Unknown service: {service_name}",
                    "response_time_ms": 0
                }
            
            # Simple health check - try to get models list
            if service_name == "ollama":
                url = f"{config['base_url']}/api/tags"
            elif service_name == "lm_studio":
                url = f"{config['base_url']}/models"
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported service for health check: {service_name}",
                    "response_time_ms": 0
                }
            
            response = await self.client.get(url, timeout=10.0)
            response.raise_for_status()
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "online",
                "response_time_ms": response_time_ms,
                "models": response.json() if response.json() else []
            }
            
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Health check failed for {service_name}: {e}")
            
            return {
                "status": "offline",
                "error": str(e),
                "response_time_ms": response_time_ms
            }
    
    async def get_available_models(self, service_name: str) -> List[str]:
        """
        Get list of available models for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of available model names
        """
        try:
            health = await self.check_service_health(service_name)
            if health["status"] == "online":
                return health.get("models", [])
            return []
        except Exception as e:
            logger.error(f"Failed to get models for {service_name}: {e}")
            return []
