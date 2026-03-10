"""
Global Search Service

Provides full-text search across all entities using PostgreSQL tsvector and pg_trgm.
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, or_, func
from sqlalchemy.orm import selectinload

from models import TestSuite, TestCase, TestExecution, User
from schemas.search import (
    SearchQuery,
    SearchResponse,
    SearchResults,
    SuiteSearchResult,
    CaseSearchResult,
    ExecutionSearchResult,
    UserSearchResult,
)
from core.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class SearchService:
    """Service for global search across entities."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.allowed_types = ["suites", "cases", "executions", "users"]

    async def global_search(self, query: SearchQuery, user_id: int) -> SearchResponse:
        """
        Perform global search across all entity types.

        Args:
            query: Search query parameters
            user_id: ID of the authenticated user

        Returns:
            SearchResponse with aggregated results
        """
        logger.info(
            "Performing global search",
            query=query.q,
            types=query.types,
            limit=query.limit,
            user_id=user_id,
        )

        # Determine which types to search
        search_types = query.types if query.types else self.allowed_types

        # Validate types
        invalid_types = [t for t in search_types if t not in self.allowed_types]
        if invalid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid search types: {invalid_types}. Allowed: {self.allowed_types}",
            )

        results = SearchResults()
        total = 0

        # Search each entity type
        if "suites" in search_types:
            suites = await self._search_suites(query.q, query.limit, user_id)
            results.suites = suites
            total += len(suites)

        if "cases" in search_types:
            cases = await self._search_cases(query.q, query.limit, user_id)
            results.cases = cases
            total += len(cases)

        if "executions" in search_types:
            executions = await self._search_executions(query.q, query.limit, user_id)
            results.executions = executions
            total += len(executions)

        if "users" in search_types:
            users = await self._search_users(query.q, query.limit, user_id)
            results.users = users
            total += len(users)

        logger.info(
            "Global search completed",
            query=query.q,
            total_results=total,
            suites=len(results.suites),
            cases=len(results.cases),
            executions=len(results.executions),
            users=len(results.users),
        )

        return SearchResponse(
            results=results,
            total=total,
            query=query.q,
            types=query.types,
            limit=query.limit,
        )

    async def _search_suites(
        self, query: str, limit: int, user_id: int
    ) -> List[SuiteSearchResult]:
        """
        Search test suites using PostgreSQL full-text search.

        Uses tsvector for fast text search and pg_trgm for fuzzy matching.
        """
        logger.debug("Searching test suites", query=query, limit=limit)

        # Try full-text search first
        search_query = text(
            """
            SELECT 
                id, 
                name, 
                description, 
                framework_type, 
                is_active, 
                created_at,
                ts_rank(
                    to_tsvector('english', name || ' ' || COALESCE(description, '')),
                    plainto_tsquery('english', :query)
                ) as relevance_score
            FROM test_suites
            WHERE 
                is_active = true
                AND to_tsvector('english', name || ' ' || COALESCE(description, '')) 
                    @@ plainto_tsquery('english', :query)
            ORDER BY relevance_score DESC
            LIMIT :limit
            """
        )

        result = await self.db.execute(
            search_query, {"query": query, "limit": limit}
        )
        rows = result.fetchall()

        # If no results, try fuzzy search with pg_trgm
        if not rows:
            logger.debug("No full-text results, trying fuzzy search")
            fuzzy_query = text(
                """
                SELECT 
                    id, 
                    name, 
                    description, 
                    framework_type, 
                    is_active, 
                    created_at,
                    similarity(name, :query) as relevance_score
                FROM test_suites
                WHERE 
                    is_active = true
                    AND similarity(name, :query) > 0.1
                ORDER BY relevance_score DESC
                LIMIT :limit
                """
            )
            result = await self.db.execute(fuzzy_query, {"query": query, "limit": limit})
            rows = result.fetchall()

        # Convert to response models
        suites = []
        for row in rows:
            suites.append(
                SuiteSearchResult(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    framework_type=row.framework_type,
                    is_active=row.is_active,
                    created_at=row.created_at,
                    relevance_score=float(row.relevance_score) if row.relevance_score else None,
                )
            )

        logger.debug("Suite search results", count=len(suites))
        return suites

    async def _search_cases(
        self, query: str, limit: int, user_id: int
    ) -> List[CaseSearchResult]:
        """
        Search test cases using PostgreSQL full-text search.
        """
        logger.debug("Searching test cases", query=query, limit=limit)

        # Full-text search on name and description
        search_query = text(
            """
            SELECT 
                tc.id, 
                tc.suite_id, 
                tc.name, 
                tc.description, 
                tc.test_type,
                tc.is_active,
                ts_rank(
                    to_tsvector('english', tc.name || ' ' || COALESCE(tc.description, '')),
                    plainto_tsquery('english', :query)
                ) as relevance_score
            FROM test_cases tc
            INNER JOIN test_suites ts ON tc.suite_id = ts.id
            WHERE 
                tc.is_active = true
                AND ts.is_active = true
                AND to_tsvector('english', tc.name || ' ' || COALESCE(tc.description, '')) 
                    @@ plainto_tsquery('english', :query)
            ORDER BY relevance_score DESC
            LIMIT :limit
            """
        )

        result = await self.db.execute(search_query, {"query": query, "limit": limit})
        rows = result.fetchall()

        # Fuzzy search fallback
        if not rows:
            logger.debug("No full-text results for cases, trying fuzzy search")
            fuzzy_query = text(
                """
                SELECT 
                    tc.id, 
                    tc.suite_id, 
                    tc.name, 
                    tc.description, 
                    tc.test_type,
                    tc.is_active,
                    similarity(tc.name, :query) as relevance_score
                FROM test_cases tc
                INNER JOIN test_suites ts ON tc.suite_id = ts.id
                WHERE 
                    tc.is_active = true
                    AND ts.is_active = true
                    AND similarity(tc.name, :query) > 0.1
                ORDER BY relevance_score DESC
                LIMIT :limit
                """
            )
            result = await self.db.execute(fuzzy_query, {"query": query, "limit": limit})
            rows = result.fetchall()

        # Convert to response models
        cases = []
        for row in rows:
            cases.append(
                CaseSearchResult(
                    id=row.id,
                    suite_id=row.suite_id,
                    name=row.name,
                    description=row.description,
                    test_type=row.test_type,
                    status="active" if row.is_active else "inactive",
                    relevance_score=float(row.relevance_score) if row.relevance_score else None,
                )
            )

        logger.debug("Case search results", count=len(cases))
        return cases

    async def _search_executions(
        self, query: str, limit: int, user_id: int
    ) -> List[ExecutionSearchResult]:
        """
        Search test executions by suite name or environment.
        """
        logger.debug("Searching test executions", query=query, limit=limit)

        # Search by suite name or environment
        search_query = text(
            """
            SELECT 
                te.id, 
                te.suite_id, 
                ts.name as suite_name, 
                te.status,
                te.environment,
                te.created_at,
                CASE 
                    WHEN te.total_tests > 0 
                    THEN (te.passed_tests::float / te.total_tests::float * 100)
                    ELSE 0 
                END as pass_rate,
                ts_rank(
                    to_tsvector('english', ts.name || ' ' || te.environment),
                    plainto_tsquery('english', :query)
                ) as relevance_score
            FROM test_executions te
            INNER JOIN test_suites ts ON te.suite_id = ts.id
            WHERE 
                to_tsvector('english', ts.name || ' ' || te.environment) 
                    @@ plainto_tsquery('english', :query)
            ORDER BY te.created_at DESC, relevance_score DESC
            LIMIT :limit
            """
        )

        result = await self.db.execute(search_query, {"query": query, "limit": limit})
        rows = result.fetchall()

        # Fuzzy search fallback
        if not rows:
            logger.debug("No full-text results for executions, trying fuzzy search")
            fuzzy_query = text(
                """
                SELECT 
                    te.id, 
                    te.suite_id, 
                    ts.name as suite_name, 
                    te.status,
                    te.environment,
                    te.created_at,
                    CASE 
                        WHEN te.total_tests > 0 
                        THEN (te.passed_tests::float / te.total_tests::float * 100)
                        ELSE 0 
                    END as pass_rate,
                    similarity(ts.name, :query) as relevance_score
                FROM test_executions te
                INNER JOIN test_suites ts ON te.suite_id = ts.id
                WHERE similarity(ts.name, :query) > 0.1
                ORDER BY te.created_at DESC, relevance_score DESC
                LIMIT :limit
                """
            )
            result = await self.db.execute(fuzzy_query, {"query": query, "limit": limit})
            rows = result.fetchall()

        # Convert to response models
        executions = []
        for row in rows:
            executions.append(
                ExecutionSearchResult(
                    id=row.id,
                    suite_id=row.suite_id,
                    suite_name=row.suite_name,
                    status=row.status,
                    pass_rate=float(row.pass_rate) if row.pass_rate else None,
                    environment=row.environment,
                    created_at=row.created_at,
                    relevance_score=float(row.relevance_score) if row.relevance_score else None,
                )
            )

        logger.debug("Execution search results", count=len(executions))
        return executions

    async def _search_users(
        self, query: str, limit: int, user_id: int
    ) -> List[UserSearchResult]:
        """
        Search users by username or email.
        """
        logger.debug("Searching users", query=query, limit=limit)

        # Search by username or email
        search_query = text(
            """
            SELECT 
                id, 
                username, 
                email, 
                is_active,
                ts_rank(
                    to_tsvector('english', username || ' ' || email),
                    plainto_tsquery('english', :query)
                ) as relevance_score
            FROM users
            WHERE 
                is_active = true
                AND to_tsvector('english', username || ' ' || email) 
                    @@ plainto_tsquery('english', :query)
            ORDER BY relevance_score DESC
            LIMIT :limit
            """
        )

        result = await self.db.execute(search_query, {"query": query, "limit": limit})
        rows = result.fetchall()

        # Fuzzy search fallback
        if not rows:
            logger.debug("No full-text results for users, trying fuzzy search")
            fuzzy_query = text(
                """
                SELECT 
                    id, 
                    username, 
                    email, 
                    is_active,
                    GREATEST(
                        similarity(username, :query),
                        similarity(email, :query)
                    ) as relevance_score
                FROM users
                WHERE 
                    is_active = true
                    AND (
                        similarity(username, :query) > 0.1
                        OR similarity(email, :query) > 0.1
                    )
                ORDER BY relevance_score DESC
                LIMIT :limit
                """
            )
            result = await self.db.execute(fuzzy_query, {"query": query, "limit": limit})
            rows = result.fetchall()

        # Convert to response models
        users = []
        for row in rows:
            users.append(
                UserSearchResult(
                    id=row.id,
                    username=row.username,
                    email=row.email,
                    is_active=row.is_active,
                    relevance_score=float(row.relevance_score) if row.relevance_score else None,
                )
            )

        logger.debug("User search results", count=len(users))
        return users

    async def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get autocomplete suggestions based on partial query.

        Uses trigram similarity to suggest matching terms.
        """
        logger.debug("Getting search suggestions", query=query, limit=limit)

        if len(query) < 2:
            return []

        suggestions = []

        # Get suggestions from suite names
        suite_query = text(
            """
            SELECT DISTINCT name
            FROM test_suites
            WHERE is_active = true
                AND similarity(name, :query) > 0.2
            ORDER BY similarity(name, :query) DESC
            LIMIT :limit
            """
        )
        result = await self.db.execute(suite_query, {"query": query, "limit": limit})
        suggestions.extend([row.name for row in result.fetchall()])

        # Get suggestions from case names
        case_query = text(
            """
            SELECT DISTINCT name
            FROM test_cases
            WHERE is_active = true
                AND similarity(name, :query) > 0.2
            ORDER BY similarity(name, :query) DESC
            LIMIT :limit
            """
        )
        result = await self.db.execute(case_query, {"query": query, "limit": limit})
        suggestions.extend([row.name for row in result.fetchall()])

        # Remove duplicates and return top suggestions
        suggestions = list(dict.fromkeys(suggestions))[:limit]

        logger.debug("Search suggestions", count=len(suggestions))
        return suggestions
