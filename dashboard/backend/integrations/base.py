"""
Base Integration Interface

All integrations must implement this interface for consistency.
Uses Adapter Pattern for different providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    UNTESTED = "untested"


class IntegrationConfig(BaseModel):
    """Base configuration for integrations"""
    enabled: bool = False
    provider: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class TestResult(BaseModel):
    """Standardized test result model"""
    test_id: str
    test_name: str
    classname: Optional[str] = None
    status: TestStatus
    duration: float = 0.0
    message: Optional[str] = None
    error: Optional[str] = None
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Jira/ALM integration fields
    issue_key: Optional[str] = None
    test_cycle_id: Optional[str] = None
    project_key: Optional[str] = None
    
    class Config:
        use_enum_values = True


class SyncResult(BaseModel):
    """Result of synchronization operation"""
    provider: str
    success: bool
    synced_count: int = 0
    failed_count: int = 0
    errors: List[str] = []
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IntegrationBase(ABC):
    """
    Abstract base class for all integrations.
    
    All integrations (Jira, Zephyr, ALM, etc.) must implement this interface
    to ensure consistency and pluggability.
    """
    
    # Class attributes (override in subclasses)
    provider_name: str = "base"
    provider_display_name: str = "Base Integration"
    provider_description: str = "Base integration provider"
    requires_auth: bool = True
    supports_sync: bool = True
    supports_test_cases: bool = True
    supports_bugs: bool = True
    supports_cycles: bool = False
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize integration with configuration.
        
        Args:
            config: Dictionary with provider-specific configuration
        """
        self.config = config
        self.is_connected = False
        self._last_error: Optional[str] = None
    
    # ==================== Connection Methods ====================
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection with the provider.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the provider.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check connection health and provider status.
        
        Returns:
            Dictionary with health status information:
            {
                "status": "healthy" | "unhealthy" | "degraded",
                "connected": bool,
                "latency_ms": int,
                "server": str,
                "user": str,
                "error": str | None
            }
        """
        pass
    
    # ==================== Synchronization Methods ====================
    
    @abstractmethod
    async def sync_test_results(
        self, 
        results: List[TestResult],
        project_key: Optional[str] = None,
        cycle_name: Optional[str] = None,
        **kwargs
    ) -> SyncResult:
        """
        Synchronize test results to the provider.
        
        Args:
            results: List of test results to sync
            project_key: Target project key
            cycle_name: Test cycle name (if supported)
            **kwargs: Provider-specific options
        
        Returns:
            SyncResult with synchronization status
        """
        pass
    
    # ==================== Test Case Methods ====================
    
    @abstractmethod
    async def create_test_case(
        self,
        name: str,
        description: str,
        project_key: str,
        folder: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a test case in the provider.
        
        Args:
            name: Test case name
            description: Test case description
            project_key: Project key
            folder: Folder/test suite path
            labels: Labels/tags for the test
            **kwargs: Provider-specific options
        
        Returns:
            Dictionary with created test case info:
            {
                "id": str,
                "key": str,
                "name": str,
                "url": str
            }
        """
        pass
    
    @abstractmethod
    async def get_test_cases(
        self,
        project_key: str,
        folder: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve test cases from the provider.
        
        Args:
            project_key: Project key
            folder: Folder/test suite path
            filters: Additional filters
        
        Returns:
            List of test case dictionaries
        """
        pass
    
    @abstractmethod
    async def update_test_case(
        self,
        test_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing test case.
        
        Args:
            test_id: Test case ID
            updates: Fields to update
        
        Returns:
            Updated test case info
        """
        pass
    
    # ==================== Bug/Defect Methods ====================
    
    @abstractmethod
    async def create_bug(
        self,
        title: str,
        description: str,
        project_key: str,
        test_result: Optional[TestResult] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a bug/defect from a failed test.
        
        Args:
            title: Bug title
            description: Bug description
            project_key: Project key
            test_result: Associated test result
            severity: Bug severity
            priority: Bug priority
            labels: Labels/tags
            **kwargs: Provider-specific options
        
        Returns:
            Dictionary with created bug info:
            {
                "id": str,
                "key": str,
                "url": str
            }
        """
        pass
    
    @abstractmethod
    async def get_bugs(
        self,
        project_key: str,
        status: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve bugs/defects from the provider.
        
        Args:
            project_key: Project key
            status: Filter by status
            filters: Additional filters
        
        Returns:
            List of bug dictionaries
        """
        pass
    
    # ==================== Project Methods ====================
    
    @abstractmethod
    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of available projects.
        
        Returns:
            List of project dictionaries:
            [
                {
                    "key": str,
                    "name": str,
                    "id": str
                }
            ]
        """
        pass
    
    # ==================== Test Cycle Methods (Optional) ====================
    
    async def create_test_cycle(
        self,
        name: str,
        project_key: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a test cycle/run (if supported).
        
        Args:
            name: Cycle name
            project_key: Project key
            description: Cycle description
            **kwargs: Provider-specific options
        
        Returns:
            Dictionary with cycle info
        
        Note:
            Override this method if provider supports test cycles
        """
        raise NotImplementedError(f"{self.provider_name} does not support test cycles")
    
    # ==================== Configuration Methods ====================
    
    @abstractmethod
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the integration configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for configuration UI.
        
        Returns:
            JSON Schema dictionary for frontend to render config form
        
        Example:
            {
                "type": "object",
                "properties": {
                    "base_url": {
                        "type": "string",
                        "title": "Server URL",
                        "format": "uri"
                    },
                    "api_token": {
                        "type": "string",
                        "title": "API Token",
                        "secret": True
                    }
                },
                "required": ["base_url", "api_token"]
            }
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider metadata.
        
        Returns:
            Dictionary with provider information
        """
        return {
            "name": self.provider_name,
            "display_name": self.provider_display_name,
            "description": self.provider_description,
            "requires_auth": self.requires_auth,
            "supports": {
                "sync": self.supports_sync,
                "test_cases": self.supports_test_cases,
                "bugs": self.supports_bugs,
                "cycles": self.supports_cycles
            },
            "config_schema": self.get_config_schema()
        }
    
    # ==================== Utility Methods ====================
    
    def _set_error(self, error: str):
        """Store last error for debugging"""
        self._last_error = error
    
    def get_last_error(self) -> Optional[str]:
        """Get last error message"""
        return self._last_error
    
    def _format_test_result_for_bug(self, result: TestResult) -> str:
        """
        Format test result into a bug description.
        
        Args:
            result: Test result to format
        
        Returns:
            Formatted string for bug description
        """
        desc = f"""**Test Failure Report**

**Test:** {result.test_name}
**Class:** {result.classname or 'N/A'}
**Status:** {result.status.value.upper()}
**Duration:** {result.duration}s
**Timestamp:** {result.timestamp.isoformat()}

**Error Message:**
{result.error or 'No error message'}

**Stack Trace:**
```
{result.stack_trace or 'No stack trace available'}
```

**Tags:** {', '.join(result.tags) if result.tags else 'None'}

**Metadata:**
```json
{result.metadata}
```
"""
        return desc.strip()
