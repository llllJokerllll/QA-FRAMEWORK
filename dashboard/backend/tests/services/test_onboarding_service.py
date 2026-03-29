"""Tests for onboarding service and API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


# --- Service Unit Tests ---

class TestOnboardingService:
    """Unit tests for onboarding_service functions."""

    def test_get_default_onboarding_state(self):
        """Default state should have 5 steps, all uncompleted."""
        from services.onboarding_service import get_default_onboarding_state
        
        state = get_default_onboarding_state()
        
        assert state["current_step"] == 0
        assert "steps" in state
        assert len(state["steps"]) == 5
        assert all(v is False for v in state["steps"].values())
        assert "welcome" in state["steps"]
        assert "connect_repo" in state["steps"]
        assert "create_suite" in state["steps"]
        assert "run_test" in state["steps"]
        assert "setup_notifications" in state["steps"]

    def _make_mock_user(self, **overrides):
        """Helper to create a mock user object."""
        user = MagicMock()
        user.id = overrides.get("id", 1)
        user.onboarding_completed = overrides.get("onboarding_completed", False)
        user.onboarding_state = overrides.get("onboarding_state", None)
        user.onboarding_completed_at = overrides.get("onboarding_completed_at", None)
        return user

    def _make_mock_db(self, user):
        """Helper to create a mock async db session that returns the given user."""
        mock_db = AsyncMock()
        # scalar_one_or_none is synchronous on SQLAlchemy result, use MagicMock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        return mock_db

    @pytest.mark.asyncio
    async def test_get_onboarding_state_new_user(self):
        """New user without onboarding_state should get defaults."""
        from services.onboarding_service import get_onboarding_state
        
        mock_user = self._make_mock_user(onboarding_state=None)
        mock_db = self._make_mock_db(mock_user)
        
        state = await get_onboarding_state(mock_db, 1)
        
        assert state["completed"] is False
        assert state["current_step"] == 0
        assert all(v is False for v in state["steps"].values())

    @pytest.mark.asyncio
    async def test_get_onboarding_state_existing_user(self):
        """User with existing state should return it."""
        from services.onboarding_service import get_onboarding_state
        
        existing_state = {
            "current_step": 2,
            "steps": {
                "welcome": True,
                "connect_repo": True,
                "create_suite": False,
                "run_test": False,
                "setup_notifications": False,
            },
        }
        mock_user = self._make_mock_user(
            onboarding_completed=False,
            onboarding_state=existing_state,
        )
        mock_db = self._make_mock_db(mock_user)
        
        state = await get_onboarding_state(mock_db, 1)
        
        assert state["completed"] is False
        assert state["current_step"] == 2
        assert state["steps"]["welcome"] is True
        assert state["steps"]["create_suite"] is False

    @pytest.mark.asyncio
    async def test_update_onboarding_step(self):
        """Updating a step should mark it completed and advance current_step."""
        from services.onboarding_service import update_onboarding_step
        
        mock_user = self._make_mock_user(onboarding_state={
            "current_step": 0,
            "steps": {
                "welcome": False,
                "connect_repo": False,
                "create_suite": False,
                "run_test": False,
                "setup_notifications": False,
            },
        })
        mock_db = self._make_mock_db(mock_user)
        
        state = await update_onboarding_step(mock_db, 1, "welcome", True)
        
        assert state["steps"]["welcome"] is True
        assert state["current_step"] == 1  # Advance to next incomplete step
        assert state["completed"] is False
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_onboarding_step_middle(self):
        """Completing a step in the middle should advance to next incomplete."""
        from services.onboarding_service import update_onboarding_step
        
        mock_user = self._make_mock_user(onboarding_state={
            "current_step": 2,
            "steps": {
                "welcome": True,
                "connect_repo": True,
                "create_suite": False,
                "run_test": False,
                "setup_notifications": False,
            },
        })
        mock_db = self._make_mock_db(mock_user)
        
        state = await update_onboarding_step(mock_db, 1, "create_suite", True)
        
        assert state["steps"]["create_suite"] is True
        assert state["current_step"] == 3  # Advance to run_test

    @pytest.mark.asyncio
    async def test_update_onboarding_invalid_step(self):
        """Updating an invalid step name should raise ValueError."""
        from services.onboarding_service import update_onboarding_step
        
        mock_user = self._make_mock_user(onboarding_state={
            "current_step": 0,
            "steps": {"welcome": False},
        })
        mock_db = self._make_mock_db(mock_user)
        
        with pytest.raises(ValueError, match="Invalid step name"):
            await update_onboarding_step(mock_db, 1, "invalid_step", True)

    @pytest.mark.asyncio
    async def test_complete_onboarding(self):
        """Completing onboarding should mark all steps and set completed flag."""
        from services.onboarding_service import complete_onboarding
        
        mock_user = self._make_mock_user(onboarding_state={
            "current_step": 0,
            "steps": {
                "welcome": True,
                "connect_repo": False,
                "create_suite": False,
                "run_test": False,
                "setup_notifications": False,
            },
        })
        mock_db = self._make_mock_db(mock_user)
        
        state = await complete_onboarding(mock_db, 1)
        
        assert state["completed"] is True
        assert all(v is True for v in state["steps"].values())
        assert state["completed_at"] is not None
        assert mock_user.onboarding_completed is True

    @pytest.mark.asyncio
    async def test_skip_onboarding(self):
        """Skipping onboarding should mark completed but keep step state as-is."""
        from services.onboarding_service import skip_onboarding
        
        mock_user = self._make_mock_user(onboarding_state={
            "current_step": 1,
            "steps": {
                "welcome": True,
                "connect_repo": False,
                "create_suite": False,
                "run_test": False,
                "setup_notifications": False,
            },
        })
        mock_db = self._make_mock_db(mock_user)
        
        state = await skip_onboarding(mock_db, 1)
        
        assert state["completed"] is True
        assert state["steps"]["welcome"] is True
        assert state["steps"]["connect_repo"] is False  # Not marked as completed
        assert mock_user.onboarding_completed is True

    @pytest.mark.asyncio
    async def test_user_not_found_get_state(self):
        """get_onboarding_state on non-existent user should raise ValueError."""
        from services.onboarding_service import get_onboarding_state
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="not found"):
            await get_onboarding_state(mock_db, 9999)

    @pytest.mark.asyncio
    async def test_user_not_found_update_step(self):
        """update_onboarding_step on non-existent user should raise ValueError."""
        from services.onboarding_service import update_onboarding_step
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="not found"):
            await update_onboarding_step(mock_db, 9999, "welcome", True)
