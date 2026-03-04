"""
Unit tests for feedback_service.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCreateFeedback:
    """Tests for create_feedback function."""

    @pytest.mark.asyncio
    async def test_create_feedback_success(self):
        from services.feedback_service import create_feedback

        mock_db = AsyncMock()
        mock_feedback_data = MagicMock()
        mock_feedback_data.feedback_type.value = "bug"
        mock_feedback_data.category = "ui"
        mock_feedback_data.title = "Button broken"
        mock_feedback_data.description = "The submit button doesn't work"
        mock_feedback_data.priority.value = "high"
        mock_feedback_data.page_url = "/dashboard"
        mock_feedback_data.browser_info = {"browser": "Chrome"}
        mock_feedback_data.rating = 2
        mock_feedback_data.tags = ["bug", "ui"]
        mock_feedback_data.attachments = []

        result = await create_feedback(
            mock_db, mock_feedback_data, user_id=1, tenant_id="t1", user_agent="Mozilla/5.0"
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_feedback_anonymous(self):
        from services.feedback_service import create_feedback

        mock_db = AsyncMock()
        mock_feedback_data = MagicMock()
        mock_feedback_data.feedback_type.value = "suggestion"
        mock_feedback_data.category = "feature"
        mock_feedback_data.title = "Add dark mode"
        mock_feedback_data.description = "Please add dark mode"
        mock_feedback_data.priority = "low"  # plain string, not enum
        mock_feedback_data.page_url = None
        mock_feedback_data.browser_info = None
        mock_feedback_data.rating = None
        mock_feedback_data.tags = None
        mock_feedback_data.attachments = None

        await create_feedback(mock_db, mock_feedback_data, user_id=None)

        mock_db.add.assert_called_once()


class TestGetFeedbackById:
    """Tests for get_feedback_by_id function."""

    @pytest.mark.asyncio
    async def test_get_feedback_found(self):
        from services.feedback_service import get_feedback_by_id

        mock_db = AsyncMock()
        mock_feedback = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feedback
        mock_db.execute.return_value = mock_result

        result = await get_feedback_by_id(mock_db, 1)
        assert result == mock_feedback

    @pytest.mark.asyncio
    async def test_get_feedback_not_found(self):
        from services.feedback_service import get_feedback_by_id

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await get_feedback_by_id(mock_db, 999)
        assert result is None


class TestListFeedback:
    """Tests for list_feedback function."""

    @pytest.mark.asyncio
    async def test_list_feedback_no_filters(self):
        from services.feedback_service import list_feedback

        mock_db = AsyncMock()

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 5

        mock_list_result = MagicMock()
        mock_feedbacks = [MagicMock(), MagicMock()]
        mock_list_result.scalars.return_value.all.return_value = mock_feedbacks

        mock_db.execute.side_effect = [mock_count_result, mock_list_result]

        results, total = await list_feedback(mock_db)

        assert results == mock_feedbacks
        assert total == 5

    @pytest.mark.asyncio
    async def test_list_feedback_with_status_filter(self):
        from services.feedback_service import list_feedback
        from schemas import FeedbackStatus

        mock_db = AsyncMock()

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        mock_list_result = MagicMock()
        mock_list_result.scalars.return_value.all.return_value = [MagicMock()]

        mock_db.execute.side_effect = [mock_count_result, mock_list_result]

        results, total = await list_feedback(mock_db, status=FeedbackStatus.new)

        assert total == 2

    @pytest.mark.asyncio
    async def test_list_feedback_empty(self):
        from services.feedback_service import list_feedback

        mock_db = AsyncMock()

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        mock_list_result = MagicMock()
        mock_list_result.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [mock_count_result, mock_list_result]

        results, total = await list_feedback(mock_db)

        assert results == []
        assert total == 0


class TestUpdateFeedback:
    """Tests for update_feedback function."""

    @pytest.mark.asyncio
    async def test_update_feedback_success(self):
        from services.feedback_service import update_feedback

        mock_db = AsyncMock()
        mock_feedback = MagicMock()
        mock_feedback.resolved_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feedback
        mock_db.execute.return_value = mock_result

        mock_update_data = MagicMock()
        mock_update_data.model_dump.return_value = {"title": "Updated Title"}

        result = await update_feedback(mock_db, 1, mock_update_data)

        assert mock_feedback.title == "Updated Title"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_feedback_not_found(self):
        from services.feedback_service import update_feedback

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        mock_update_data = MagicMock()
        mock_update_data.model_dump.return_value = {}

        result = await update_feedback(mock_db, 999, mock_update_data)

        assert result is None
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_feedback_sets_resolved_at(self):
        from services.feedback_service import update_feedback
        from schemas import FeedbackStatus

        mock_db = AsyncMock()
        mock_feedback = MagicMock()
        mock_feedback.resolved_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feedback
        mock_db.execute.return_value = mock_result

        mock_update_data = MagicMock()
        mock_update_data.model_dump.return_value = {"status": FeedbackStatus.resolved}

        await update_feedback(mock_db, 1, mock_update_data)

        assert mock_feedback.resolved_at is not None


class TestDeleteFeedback:
    """Tests for delete_feedback function."""

    @pytest.mark.asyncio
    async def test_delete_feedback_success(self):
        from services.feedback_service import delete_feedback

        mock_db = AsyncMock()
        mock_feedback = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feedback
        mock_db.execute.return_value = mock_result

        result = await delete_feedback(mock_db, 1)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_feedback)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_feedback_not_found(self):
        from services.feedback_service import delete_feedback

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await delete_feedback(mock_db, 999)

        assert result is False
        mock_db.delete.assert_not_called()


class TestGetFeedbackStats:
    """Tests for get_feedback_stats function."""

    @pytest.mark.asyncio
    async def test_get_stats_basic(self):
        from services.feedback_service import get_feedback_stats

        mock_db = AsyncMock()

        # total, by_status, by_type, avg_rating
        mock_total = MagicMock(); mock_total.scalar.return_value = 10
        mock_status = MagicMock(); mock_status.__iter__ = MagicMock(return_value=iter([]))
        mock_type = MagicMock(); mock_type.__iter__ = MagicMock(return_value=iter([]))
        mock_rating = MagicMock(); mock_rating.scalar.return_value = 4.2

        mock_db.execute.side_effect = [mock_total, mock_status, mock_type, mock_rating]

        result = await get_feedback_stats(mock_db)

        assert result["total"] == 10
        assert result["average_rating"] == 4.2

    @pytest.mark.asyncio
    async def test_get_stats_no_ratings(self):
        from services.feedback_service import get_feedback_stats

        mock_db = AsyncMock()

        mock_total = MagicMock(); mock_total.scalar.return_value = 5
        mock_status = MagicMock(); mock_status.__iter__ = MagicMock(return_value=iter([]))
        mock_type = MagicMock(); mock_type.__iter__ = MagicMock(return_value=iter([]))
        mock_rating = MagicMock(); mock_rating.scalar.return_value = None

        mock_db.execute.side_effect = [mock_total, mock_status, mock_type, mock_rating]

        result = await get_feedback_stats(mock_db)

        assert result["average_rating"] is None

    @pytest.mark.asyncio
    async def test_get_stats_with_tenant_id(self):
        from services.feedback_service import get_feedback_stats

        mock_db = AsyncMock()

        mock_total = MagicMock(); mock_total.scalar.return_value = 3
        mock_status = MagicMock(); mock_status.__iter__ = MagicMock(return_value=iter([]))
        mock_type = MagicMock(); mock_type.__iter__ = MagicMock(return_value=iter([]))
        mock_rating = MagicMock(); mock_rating.scalar.return_value = None

        mock_db.execute.side_effect = [mock_total, mock_status, mock_type, mock_rating]

        result = await get_feedback_stats(mock_db, tenant_id="tenant-abc")

        assert result["total"] == 3
