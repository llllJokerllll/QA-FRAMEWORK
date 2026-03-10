"""
Search API Routes

Provides global search endpoint with full-text search capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db_session as get_db
from services.auth_service import get_current_user
from services.search_service import SearchService
from schemas.search import (
    SearchQuery,
    SearchResponse,
    SearchSuggestions,
)
from models import User
from core.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query string"),
    types: Optional[str] = Query(
        None,
        description="Comma-separated list of entity types (suites,cases,executions,users)"
    ),
    limit: int = Query(10, ge=1, le=50, description="Max results per type"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Global search across all entities.

    Performs full-text search across test suites, test cases, executions, and users.
    Uses PostgreSQL tsvector for fast text search and pg_trgm for fuzzy matching.

    **Query Parameters:**
    - `q`: Search query string (required)
    - `types`: Comma-separated filter by entity types (optional)
      - Allowed values: `suites`, `cases`, `executions`, `users`
      - Example: `suites,cases`
    - `limit`: Maximum results per type (default: 10, max: 50)

    **Authentication:** Required

    **Response:**
    Returns search results grouped by entity type with relevance scores.

    **Example:**
    ```
    GET /api/v1/search?q=login&types=suites,cases&limit=10

    Response:
    {
      "results": {
        "suites": [
          {
            "id": 123,
            "name": "Login Tests",
            "description": "Authentication test suite",
            "framework_type": "playwright",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z",
            "relevance_score": 0.85
          }
        ],
        "cases": [...],
        "executions": [],
        "users": []
      },
      "total": 5,
      "query": "login",
      "types": ["suites", "cases"],
      "limit": 10
    }
    ```
    """
    logger.info(
        "Global search request",
        query=q,
        types=types,
        limit=limit,
        offset=offset,
        user_id=current_user.id,
    )

    try:
        # Parse types parameter
        type_list = None
        if types:
            type_list = [t.strip().lower() for t in types.split(",")]

        # Create search query
        search_query = SearchQuery(q=q, types=type_list, limit=limit, offset=offset)

        # Perform search
        search_service = SearchService(db)
        response = await search_service.global_search(search_query, current_user.id)

        logger.info(
            "Search completed successfully",
            query=q,
            total_results=response.total,
            user_id=current_user.id,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Search failed",
            query=q,
            error=str(e),
            user_id=current_user.id,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed",
        )


@router.get("/suggestions", response_model=SearchSuggestions)
async def get_search_suggestions(
    q: str = Query(..., min_length=2, max_length=200, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get autocomplete suggestions for search queries.

    Returns suggested search terms based on partial input using trigram similarity.

    **Query Parameters:**
    - `q`: Partial search query (min 2 characters)
    - `limit`: Number of suggestions (default: 5, max: 10)

    **Authentication:** Required

    **Response:**
    Returns list of suggested search terms.

    **Example:**
    ```
    GET /api/v1/search/suggestions?q=log&limit=5

    Response:
    {
      "suggestions": [
        "Login Tests",
        "Logout Flow",
        "Logger Integration"
      ],
      "query": "log"
    }
    ```
    """
    logger.info(
        "Search suggestions request",
        query=q,
        limit=limit,
        user_id=current_user.id,
    )

    try:
        search_service = SearchService(db)
        suggestions = await search_service.get_search_suggestions(q, limit)

        logger.info(
            "Suggestions retrieved",
            query=q,
            count=len(suggestions),
            user_id=current_user.id,
        )

        return SearchSuggestions(suggestions=suggestions, query=q)

    except Exception as e:
        logger.error(
            "Failed to get suggestions",
            query=q,
            error=str(e),
            user_id=current_user.id,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search suggestions",
        )
