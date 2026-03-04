"""
Unit tests for case_service.py

Tests all test case management functions with mocked DB and cache.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def mock_cache_manager():
    """Mock cache_manager for all case service tests."""
    with patch("services.case_service.cache_manager") as mock_cache:
        mock_cache.async_get = AsyncMock(return_value=None)
        mock_cache.async_set = AsyncMock()
        mock_cache.get_case_list_key = MagicMock(return_value="case:list:None:0:100")
        mock_cache.get_case_key = MagicMock(return_value="case:1")
        mock_cache.invalidate_case_cache = AsyncMock()
        yield mock_cache


class TestCreateCaseService:
    """Tests for create_case_service function."""

    @pytest.mark.asyncio
    async def test_create_case_success(self, mock_cache_manager):
        """Test successful test case creation."""
        from services.case_service import create_case_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()
        mock_suite.id = 1

        mock_case_data = MagicMock()
        mock_case_data.suite_id = 1
        mock_case_data.name = "Test Login"
        mock_case_data.description = "Test user login flow"
        mock_case_data.test_code = "def test_login(): pass"
        mock_case_data.test_type = "functional"
        mock_case_data.priority = "high"
        mock_case_data.tags = ["auth", "login"]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await create_case_service(mock_case_data, mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        mock_cache_manager.invalidate_case_cache.assert_called_once_with(suite_id=1)

    @pytest.mark.asyncio
    async def test_create_case_suite_not_found(self, mock_cache_manager):
        """Test case creation fails when suite not found."""
        from services.case_service import create_case_service

        mock_db = AsyncMock()
        mock_case_data = MagicMock()
        mock_case_data.suite_id = 999
        mock_case_data.name = "My Case"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Suite not found
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await create_case_service(mock_case_data, mock_db)

        assert exc_info.value.status_code == 404
        assert "Test suite not found" in str(exc_info.value.detail)
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_case_minimal_data(self, mock_cache_manager):
        """Test creating a case with minimal required data."""
        from services.case_service import create_case_service

        mock_db = AsyncMock()
        mock_suite = MagicMock()

        mock_case_data = MagicMock()
        mock_case_data.suite_id = 1
        mock_case_data.name = "Simple Test"
        mock_case_data.description = None
        mock_case_data.test_code = None
        mock_case_data.test_type = "unit"
        mock_case_data.priority = "medium"
        mock_case_data.tags = []

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suite
        mock_db.execute.return_value = mock_result

        await create_case_service(mock_case_data, mock_db)

        mock_db.add.assert_called_once()


class TestListCasesService:
    """Tests for list_cases_service function."""

    @pytest.mark.asyncio
    async def test_list_cases_no_filter_from_db(self, mock_cache_manager):
        """Test listing all cases from DB (no suite filter)."""
        from services.case_service import list_cases_service

        mock_db = AsyncMock()
        mock_cases = [MagicMock(), MagicMock()]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_cases
        mock_db.execute.return_value = mock_result

        result = await list_cases_service(db=mock_db)

        assert result == mock_cases
        mock_cache_manager.async_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_cases_with_suite_filter(self, mock_cache_manager):
        """Test listing cases filtered by suite ID."""
        from services.case_service import list_cases_service

        mock_db = AsyncMock()
        mock_cases = [MagicMock()]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_cases
        mock_db.execute.return_value = mock_result

        mock_cache_manager.get_case_list_key.return_value = "case:list:5:0:100"

        result = await list_cases_service(suite_id=5, db=mock_db)

        assert result == mock_cases
        mock_cache_manager.get_case_list_key.assert_called_with(5, 0, 100)

    @pytest.mark.asyncio
    async def test_list_cases_from_cache(self, mock_cache_manager):
        """Test listing cases from cache."""
        from services.case_service import list_cases_service

        cached_cases = [MagicMock(), MagicMock(), MagicMock()]
        mock_cache_manager.async_get.return_value = cached_cases

        mock_db = AsyncMock()

        result = await list_cases_service(db=mock_db)

        assert result == cached_cases
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_cases_empty(self, mock_cache_manager):
        """Test listing when no cases exist."""
        from services.case_service import list_cases_service

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await list_cases_service(db=mock_db)

        assert result == []

    @pytest.mark.asyncio
    async def test_list_cases_pagination(self, mock_cache_manager):
        """Test listing cases with pagination."""
        from services.case_service import list_cases_service

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        mock_cache_manager.get_case_list_key.return_value = "case:list:None:20:10"

        await list_cases_service(skip=20, limit=10, db=mock_db)

        mock_cache_manager.get_case_list_key.assert_called_with(None, 20, 10)


class TestGetCaseById:
    """Tests for get_case_by_id function."""

    @pytest.mark.asyncio
    async def test_get_case_from_db(self, mock_cache_manager):
        """Test getting case from database (cache miss)."""
        from services.case_service import get_case_by_id

        mock_db = AsyncMock()
        mock_case = MagicMock()
        mock_case.id = 1
        mock_case.name = "Login Test"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_db.execute.return_value = mock_result

        result = await get_case_by_id(1, mock_db)

        assert result == mock_case
        mock_cache_manager.async_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_case_from_cache(self, mock_cache_manager):
        """Test getting case from cache (cache hit)."""
        from services.case_service import get_case_by_id

        cached_case = MagicMock()
        mock_cache_manager.async_get.return_value = cached_case

        mock_db = AsyncMock()

        result = await get_case_by_id(1, mock_db)

        assert result == cached_case
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_case_not_found(self, mock_cache_manager):
        """Test 404 when case not found."""
        from services.case_service import get_case_by_id

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_case_by_id(999, mock_db)

        assert exc_info.value.status_code == 404
        assert "Test case not found" in str(exc_info.value.detail)


class TestUpdateCaseService:
    """Tests for update_case_service function."""

    @pytest.mark.asyncio
    async def test_update_case_name(self, mock_cache_manager):
        """Test updating case name."""
        from services.case_service import update_case_service

        mock_db = AsyncMock()
        mock_case = MagicMock()
        mock_case.suite_id = 1

        mock_case_update = MagicMock()
        mock_case_update.name = "New Name"
        mock_case_update.description = None
        mock_case_update.test_code = None
        mock_case_update.test_type = None
        mock_case_update.priority = None
        mock_case_update.tags = None
        mock_case_update.is_active = None
        mock_case_update.model_dump = MagicMock(return_value={"name": "New Name"})

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_db.execute.return_value = mock_result

        await update_case_service(1, mock_case_update, mock_db)

        assert mock_case.name == "New Name"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_case_all_fields(self, mock_cache_manager):
        """Test updating all case fields."""
        from services.case_service import update_case_service

        mock_db = AsyncMock()
        mock_case = MagicMock()
        mock_case.suite_id = 3

        mock_case_update = MagicMock()
        mock_case_update.name = "Updated Name"
        mock_case_update.description = "Updated Desc"
        mock_case_update.test_code = "def test(): assert True"
        mock_case_update.test_type = "integration"
        mock_case_update.priority = "critical"
        mock_case_update.tags = ["smoke", "regression"]
        mock_case_update.is_active = False
        mock_case_update.model_dump = MagicMock(return_value={
            "name": "Updated Name",
            "description": "Updated Desc",
        })

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_db.execute.return_value = mock_result

        await update_case_service(1, mock_case_update, mock_db)

        assert mock_case.name == "Updated Name"
        assert mock_case.description == "Updated Desc"
        assert mock_case.test_code == "def test(): assert True"
        assert mock_case.test_type == "integration"
        assert mock_case.priority == "critical"
        assert mock_case.tags == ["smoke", "regression"]
        assert mock_case.is_active == False

    @pytest.mark.asyncio
    async def test_update_case_not_found(self, mock_cache_manager):
        """Test update fails when case not found."""
        from services.case_service import update_case_service

        mock_db = AsyncMock()
        mock_case_update = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await update_case_service(999, mock_case_update, mock_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_case_cache_invalidated(self, mock_cache_manager):
        """Test cache is invalidated with correct IDs on update."""
        from services.case_service import update_case_service

        mock_db = AsyncMock()
        mock_case = MagicMock()
        mock_case.suite_id = 5

        mock_case_update = MagicMock()
        mock_case_update.name = "Updated"
        mock_case_update.description = None
        mock_case_update.test_code = None
        mock_case_update.test_type = None
        mock_case_update.priority = None
        mock_case_update.tags = None
        mock_case_update.is_active = None
        mock_case_update.model_dump = MagicMock(return_value={})

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_db.execute.return_value = mock_result

        await update_case_service(3, mock_case_update, mock_db)

        mock_cache_manager.invalidate_case_cache.assert_called_with(3, 5)


class TestDeleteCaseService:
    """Tests for delete_case_service function."""

    @pytest.mark.asyncio
    async def test_delete_case_success(self, mock_cache_manager):
        """Test successful case soft delete."""
        from services.case_service import delete_case_service

        mock_db = AsyncMock()
        mock_case = MagicMock()
        mock_case.is_active = True
        mock_case.suite_id = 2

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_db.execute.return_value = mock_result

        await delete_case_service(1, mock_db)

        assert mock_case.is_active == False
        mock_db.commit.assert_called_once()
        mock_cache_manager.invalidate_case_cache.assert_called()

    @pytest.mark.asyncio
    async def test_delete_case_not_found(self, mock_cache_manager):
        """Test delete fails when case not found."""
        from services.case_service import delete_case_service

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await delete_case_service(999, mock_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_case_cache_invalidated_with_suite_id(self, mock_cache_manager):
        """Test cache invalidated with both case_id and suite_id."""
        from services.case_service import delete_case_service

        mock_db = AsyncMock()
        mock_case = MagicMock()
        mock_case.is_active = True
        mock_case.suite_id = 7

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_case
        mock_db.execute.return_value = mock_result

        await delete_case_service(4, mock_db)

        mock_cache_manager.invalidate_case_cache.assert_called_with(4, 7)
