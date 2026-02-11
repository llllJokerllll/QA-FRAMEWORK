"""Interfaces - Contracts for core components (SOLID DIP)"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.core.entities.test_result import TestResult


class ITestRunner(ABC):
    """Interface for test runner (Dependency Inversion Principle)"""
    
    @abstractmethod
    async def run_test(self, test_func: Any, *args, **kwargs) -> TestResult:
        """
        Run a test function.
        
        Args:
            test_func: Test function to execute
            *args: Positional arguments for test function
            **kwargs: Keyword arguments for test function
            
        Returns:
            TestResult object with execution details
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources after test execution"""
        pass


class IHTTPClient(ABC):
    """Interface for HTTP client adapters"""
    
    @abstractmethod
    async def get(self, url: str, **kwargs) -> Any:
        """Perform GET request"""
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """Perform POST request"""
        pass
    
    @abstractmethod
    async def put(self, url: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """Perform PUT request"""
        pass
    
    @abstractmethod
    async def delete(self, url: str, **kwargs) -> Any:
        """Perform DELETE request"""
        pass


class IUIPage(ABC):
    """
    Interface for UI page objects (Single Responsibility Principle).
    
    This interface defines the contract for all UI page adapters,
    following the Interface Segregation Principle (ISP) from SOLID.
    """
    
    @abstractmethod
    async def goto(self, url: str) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
        """
        pass
    
    @abstractmethod
    async def click(self, selector: str) -> None:
        """
        Click on an element.
        
        Args:
            selector: CSS selector for the element
        """
        pass
    
    @abstractmethod
    async def fill(self, selector: str, value: str) -> None:
        """
        Fill an input field with a value.
        
        Args:
            selector: CSS selector for the input
            value: Value to fill
        """
        pass
    
    @abstractmethod
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector for the element
            timeout: Timeout in milliseconds (default: 30000)
        """
        pass
    
    @abstractmethod
    async def get_text(self, selector: str) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            Text content of the element
        """
        pass
    
    @abstractmethod
    async def is_visible(self, selector: str) -> bool:
        """
        Check if an element is visible.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            True if visible, False otherwise
        """
        pass
    
    @abstractmethod
    async def screenshot(self, path: str) -> None:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Path to save the screenshot
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the browser/page."""
        pass


class IAssertion(ABC):
    """Interface for assertions (Interface Segregation Principle)"""
    
    @abstractmethod
    def assert_equal(self, actual: Any, expected: Any, message: Optional[str] = None) -> None:
        """Assert two values are equal"""
        pass
    
    @abstractmethod
    def assert_true(self, condition: bool, message: Optional[str] = None) -> None:
        """Assert condition is true"""
        pass
    
    @abstractmethod
    def assert_status_code(self, response: Any, expected: int) -> None:
        """Assert HTTP status code"""
        pass
