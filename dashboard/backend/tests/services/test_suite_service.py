"""
Unit tests for suite_service.py

Tests all test suite management functions with mocked DB and cache.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def mock_cache_manager():
    """Mock cache_manager for all suite service tests."""
    with patch("services.suite_service.cache_manager") as mock_cache:
        mock_cache.async_get = AsyncMock(return_value=None)  # Cache miss by default
        mock_cache.async_set = AsyncMock()
        mock_cache.get_suite_list_key = MagicMock(return_value="suite:list:0:100")
        mock_cache.get_suite_key = MagicMock(return_value="suite:1")
        mock_cache.invalidate_suite_cache = AsyncMock()
        yield mock_cache


class TestCreateSuiteService:
    """Tests for create_suite_service function."""

    @pytest.mark.asyncio
    async def test_create_suite_success(self, mock_cache_manager):
        """Test successful suite creation."""
        from services.suite_service import create_suite_service

        mock_db = AsyncMock()
        mock_suite_data = MagicMock()
        mock_suite_data.name = "My Test Suite"
        mock_suite_data.description = "A test suite"
        mock_suite_data.framework_type = "pytest"
        mock_suite_data.config = {}

        await create_suite_service(mock_suite_data, user_id=1, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        mock_cache_manager.invalidate_suite_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_suite_with_config(self, mock_cache_manager):
        """Test suite creation with custom config."""
        from services.suite_service import create_suite_service

        mock_db = AsyncMock()
        mock_suite_data = MagicMock()
        mock_suite_data.name = "Configured Suite"
        mock_suite_data.description = None
        mock_suite_data.framework_type = "jest"
        mock_suite_data.config = {"timeout": 5000, "retries": 3}

        await create_suite_service(mock_suite_data, user_id=42, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_suite_cache_invalidated(self, mock_cache_manager):
        """Test that cache is invalidated after creation."""
        from services.suite_service import create_suite_service

        mock_db = AsyncMock()
        mock_suite_data = MagicMock()
        mock_suite_data.name = "New Suite"
        mock_suite_data.description = ""
        mock_suite_data.framework_type = "pytest"
        mock_suite_data.config = None

        await create_suite_service(mock_suite_data, user_id=1, db=mock_db)

        mock_cache_manager.invalidate_suite_cache.assert_called_once_with()


class TestListSuitesService:
    """Tests for list_suites_service function."""

    @pytest.mark.asyncio
    async def test_list_suites_from_db(self, mock_cache_manager):
        """Test listing suites from database (cache miss)."""
        from services.suite_service import list_suites_service

        mock_db = AsyncMock()
        mock_suites = [MagicMock(), MagicMock()]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_suites
        mock_db.execute.return_value = mock_result

        result = await list_suites_service(skip=0, limit=100, db=mock_db)

        assert result == mock_suites
        mock_cache_manager.async_set.assert_called_once()  # Cached after fetch

    @pytest.mark.asyncio
    async def test_list_suites_from_cache(self, mock_cache_manager):
        """Test listing suites from cache (cache hit)."""
        from services.suite_service import list_suites_service

        cached_suites = [MagicMock(), MagicMock(), MagicMock()]
        mock_cache_manager.async_get.return_value = cached_suites

        mock_db = AsyncMock()

        result = await list_suites_service(db=mock_db)

        assert result == cached_suites
        mock_db.execute.assert_not_called()  # DB not queried on cache hit

    @pytest.mark.asyncio
    async def test_list_suites_empty(self, mock_cache_manager):
        """Test listing when no suites exist."""
        from services.suite_service import list_suites_service

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await list_suites_service(db=mock_db)

        assert result == []

    @pytest.mark.asyncio
    async def test_list_suites_pagination(self, mock_cache_manager):
        """Test listing suites with pagination."""
        from services.suite_service import list_suites_service

        mock_db = AsyncMock()
        mock_suites = [MagicMock()]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_suites
        mock_db.execute.return_value = mock_result

        mock_cache_manager.get_suite_list_key.return_value = "suite:list:10:5"

        result = await list_suites_service(skip=10, limit=5, db=mock_db)

        assert result == mock_suites
        mock_cache_manager.get_suite_list_key.assert_called_with(10, 5)


class TestGetSuiteById:
    """Tests for get_suite_by_id function."""

    @pytest.mark.asyncio
    async def test_get_suite_from_db(self, mock_cache_manager):
        """Test getting suite from database (cache miss)."""
        from services.suite_service import get_suite_by_id

        mock_db = AsyncMock()
        mock_suite = MagicMock()
        mock_suite.id = 1
        mock_suite.name = "My Suite"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        result = await get_suite_by_id(1, mock_db)

        assert result == mock_suite
        mock_cache_manager.async_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_suite_from_cache(self, mock_cache_manager):
        """Test getting suite from cache (cache hit)."""
        from services.suite_service import get_suite_by_id

        cached_suite = MagicMock()
        mock_cache_manager.async_get.return_value = cached_suite

        mock_db = AsyncMock()

        result = await get_suite_by_id(1, mock_db)

        assert result == cached_suite
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_suite_not_found(self, mock_cache_manager):
        """Test 404 when suite not found."""
        from services.suite_service import get_suite_by_id

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_suite_by_id(999, mock_db)

        assert exc_info.value.status_code == 404
        assert "Test suite not found" in str(exc_info.value.detail)


class TestUpdateSuiteService:
    """Tests for update_suite_service function."""

    @pytest.mark.asyncio
    async def test_update_suite_name(self, mock_cache_manager):
        """Test updating suite name."""
        from services.suite_service import update_suite_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()
        mock_suite.name = "Old Name"
        mock_suite.description = "desc"
        mock_suite.framework_type = "pytest"
        mock_suite.config = {}
        mock_suite.is_active = True

        mock_suite_update = MagicMock()
        mock_suite_update.name = "New Name"
        mock_suite_update.description = None
        mock_suite_update.framework_type = None
        mock_suite_update.config = None
        mock_suite_update.is_active = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await update_suite_service(1, mock_suite_update, mock_db)

        assert mock_suite.name == "New Name"
        mock_db.commit.assert_called_once()
        mock_cache_manager.invalidate_suite_cache.assert_called_with(1)

    @pytest.mark.asyncio
    async def test_update_suite_all_fields(self, mock_cache_manager):
        """Test updating all suite fields."""
        from services.suite_service import update_suite_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()

        mock_suite_update = MagicMock()
        mock_suite_update.name = "New Name"
        mock_suite_update.description = "New Desc"
        mock_suite_update.framework_type = "jest"
        mock_suite_update.config = {"key": "val"}
        mock_suite_update.is_active = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await update_suite_service(1, mock_suite_update, mock_db)

        assert mock_suite.name == "New Name"
        assert mock_suite.description == "New Desc"
        assert mock_suite.framework_type == "jest"
        assert mock_suite.config == {"key": "val"}
        assert mock_suite.is_active == False

    @pytest.mark.asyncio
    async def test_update_suite_not_found(self, mock_cache_manager):
        """Test update fails when suite not found."""
        from services.suite_service import update_suite_service

        mock_db = AsyncMock()
        mock_suite_update = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await update_suite_service(999, mock_suite_update, mock_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_suite_cache_invalidated(self, mock_cache_manager):
        """Test that specific suite cache is invalidated on update."""
        from services.suite_service import update_suite_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()

        mock_suite_update = MagicMock()
        mock_suite_update.name = "Updated"
        mock_suite_update.description = None
        mock_suite_update.framework_type = None
        mock_suite_update.config = None
        mock_suite_update.is_active = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await update_suite_service(5, mock_suite_update, mock_db)

        mock_cache_manager.invalidate_suite_cache.assert_called_with(5)


class TestDeleteSuiteService:
    """Tests for delete_suite_service function."""

    @pytest.mark.asyncio
    async def test_delete_suite_success(self, mock_cache_manager):
        """Test successful suite soft delete."""
        from services.suite_service import delete_suite_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()
        mock_suite.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await delete_suite_service(1, mock_db)

        assert mock_suite.is_active == False
        mock_db.commit.assert_called_once()
        mock_cache_manager.invalidate_suite_cache.assert_called_with(1)

    @pytest.mark.asyncio
    async def test_delete_suite_not_found(self, mock_cache_manager):
        """Test delete fails when suite not found."""
        from services.suite_service import delete_suite_service

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await delete_suite_service(999, mock_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_already_inactive(self, mock_cache_manager):
        """Test soft-deleting an already inactive suite."""
        from services.suite_service import delete_suite_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()
        mock_suite.is_active = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await delete_suite_service(1, mock_db)

        assert mock_suite.is_active == False
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_cache_invalidated_for_suite(self, mock_cache_manager):
        """Test that suite-specific cache is invalidated on delete."""
        from services.suite_service import delete_suite_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()
        mock_suite.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await delete_suite_service(7, mock_db)

        mock_cache_manager.invalidate_suite_cache.assert_called_with(7)
