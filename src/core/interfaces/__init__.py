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
    """Interface for UI page objects (Single Responsibility Principle)"""
    
    @abstractmethod
    async def goto(self, url: str) -> None:
        """Navigate to URL"""
        pass
    
    @abstractmethod
    async def click(self, selector: str) -> None:
        """Click element"""
        pass
    
    @abstractmethod
    async def fill(self, selector: str, value: str) -> None:
        """Fill input field"""
        pass
    
    @abstractmethod
    async def expect_visible(self, selector: str) -> bool:
        """Expect element to be visible"""
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
