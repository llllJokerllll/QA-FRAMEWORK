"""Search schemas for global search functionality."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SearchQuery(BaseModel):
    """Search query parameters."""
    q: str = Field(..., min_length=1, max_length=200, description="Search query string")
    types: Optional[List[str]] = Field(
        default=None,
        description="Filter by entity types (suites, cases, executions, users)"
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max results per type")
    offset: int = Field(default=0, ge=0, description="Number of results to skip for pagination")


class SuiteSearchResult(BaseModel):
    """Search result for test suite."""
    id: int
    name: str
    description: Optional[str] = None
    framework_type: str
    is_active: bool
    created_at: datetime
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True


class CaseSearchResult(BaseModel):
    """Search result for test case."""
    id: int
    suite_id: int
    name: str
    description: Optional[str] = None
    test_type: str
    status: str = "active"
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True


class ExecutionSearchResult(BaseModel):
    """Search result for test execution."""
    id: int
    suite_id: int
    suite_name: str
    status: str
    pass_rate: Optional[float] = None
    environment: str
    created_at: datetime
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True


class UserSearchResult(BaseModel):
    """Search result for user."""
    id: int
    username: str
    email: str
    is_active: bool
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    """Aggregated search results."""
    suites: List[SuiteSearchResult] = []
    cases: List[CaseSearchResult] = []
    executions: List[ExecutionSearchResult] = []
    users: List[UserSearchResult] = []


class SearchResponse(BaseModel):
    """Complete search response."""
    results: SearchResults
    total: int
    query: str
    types: Optional[List[str]] = None
    limit: int
    offset: int = 0


class SearchSuggestions(BaseModel):
    """Search autocomplete suggestions."""
    suggestions: List[str]
    query: str
