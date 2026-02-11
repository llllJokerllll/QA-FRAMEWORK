"""HTTP Client adapter using HTTPX (async)"""

import httpx
from typing import Any, Dict, Optional
from src.core.interfaces import IHTTPClient


class HTTPXClient(IHTTPClient):
    """
    Async HTTP client using HTTPX library.
    
    This adapter implements the IHTTPClient interface, following
    the Dependency Inversion Principle (DIP) from SOLID.
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize HTTPX client.
        
        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            headers: Default headers for all requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTPX client (Singleton pattern for connection pooling)"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers
            )
        return self._client
    
    async def get(self, url: str, **kwargs) -> Any:
        """
        Perform GET request.
        
        Args:
            url: Endpoint URL (relative to base_url)
            **kwargs: Additional httpx arguments
            
        Returns:
            Response object with status_code, json() method
        """
        client = await self._get_client()
        response = await client.get(url, **kwargs)
        return response
    
    async def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """
        Perform POST request.
        
        Args:
            url: Endpoint URL
            data: Request body data
            **kwargs: Additional httpx arguments
            
        Returns:
            Response object
        """
        client = await self._get_client()
        response = await client.post(url, json=data, **kwargs)
        return response
    
    async def put(self, url: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """
        Perform PUT request.
        
        Args:
            url: Endpoint URL
            data: Request body data
            **kwargs: Additional httpx arguments
            
        Returns:
            Response object
        """
        client = await self._get_client()
        response = await client.put(url, json=data, **kwargs)
        return response
    
    async def delete(self, url: str, **kwargs) -> Any:
        """
        Perform DELETE request.
        
        Args:
            url: Endpoint URL
            **kwargs: Additional httpx arguments
            
        Returns:
            Response object
        """
        client = await self._get_client()
        response = await client.delete(url, **kwargs)
        return response
    
    async def close(self) -> None:
        """Close HTTPX client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
