"""
Unit tests for beta_signup_service.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCreateBetaSignup:
    @pytest.mark.asyncio
    async def test_create_signup_success(self):
        from services.beta_signup_service import create_beta_signup

        mock_db = AsyncMock()
        mock_data = MagicMock()
        mock_data.email = "user@example.com"
        mock_data.company = "Acme Corp"
        mock_data.use_case = "CI/CD automation"
        mock_data.team_size.value = "11-50"
        mock_data.source = "landing_page"
        mock_data.utm_campaign = "spring2026"
        mock_data.utm_source = "google"

        await create_beta_signup(mock_db, mock_data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_signup_minimal(self):
        from services.beta_signup_service import create_beta_signup

        mock_db = AsyncMock()
        mock_data = MagicMock()
        mock_data.email = "minimal@test.com"
        mock_data.company = None
        mock_data.use_case = None
        mock_data.team_size = "1-10"  # plain string, not enum
        mock_data.source = None
        mock_data.utm_campaign = None
        mock_data.utm_source = None

        await create_beta_signup(mock_db, mock_data)

        mock_db.add.assert_called_once()


class TestGetBetaSignup:
    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        from services.beta_signup_service import get_beta_signup_by_id

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        result = await get_beta_signup_by_id(mock_db, 1)
        assert result == mock_signup

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        from services.beta_signup_service import get_beta_signup_by_id

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await get_beta_signup_by_id(mock_db, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_found(self):
        from services.beta_signup_service import get_beta_signup_by_email

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        result = await get_beta_signup_by_email(mock_db, "user@test.com")
        assert result == mock_signup

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self):
        from services.beta_signup_service import get_beta_signup_by_email

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await get_beta_signup_by_email(mock_db, "nobody@nowhere.com")
        assert result is None


class TestListBetaSignups:
    @pytest.mark.asyncio
    async def test_list_no_filters(self):
        from services.beta_signup_service import list_beta_signups

        mock_db = AsyncMock()
        mock_count = MagicMock(); mock_count.scalar.return_value = 3
        mock_list = MagicMock()
        mock_list.scalars.return_value.all.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_db.execute.side_effect = [mock_count, mock_list]

        results, total = await list_beta_signups(mock_db)
        assert total == 3
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_list_with_status_filter(self):
        from services.beta_signup_service import list_beta_signups
        from schemas import BetaSignupStatus

        mock_db = AsyncMock()
        mock_count = MagicMock(); mock_count.scalar.return_value = 1
        mock_list = MagicMock()
        mock_list.scalars.return_value.all.return_value = [MagicMock()]
        mock_db.execute.side_effect = [mock_count, mock_list]

        results, total = await list_beta_signups(mock_db, status=BetaSignupStatus.approved)
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_empty(self):
        from services.beta_signup_service import list_beta_signups

        mock_db = AsyncMock()
        mock_count = MagicMock(); mock_count.scalar.return_value = 0
        mock_list = MagicMock()
        mock_list.scalars.return_value.all.return_value = []
        mock_db.execute.side_effect = [mock_count, mock_list]

        results, total = await list_beta_signups(mock_db)
        assert total == 0
        assert results == []


class TestUpdateBetaSignup:
    @pytest.mark.asyncio
    async def test_update_success(self):
        from services.beta_signup_service import update_beta_signup

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_signup.invite_sent_at = None
        mock_signup.onboarded_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        mock_update = MagicMock()
        mock_update.model_dump.return_value = {"company": "New Corp"}

        result = await update_beta_signup(mock_db, 1, mock_update)

        assert mock_signup.company == "New Corp"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        from services.beta_signup_service import update_beta_signup

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        mock_update = MagicMock()
        mock_update.model_dump.return_value = {}

        result = await update_beta_signup(mock_db, 999, mock_update)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_sets_invite_sent_at_on_approve(self):
        from services.beta_signup_service import update_beta_signup
        from schemas import BetaSignupStatus

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_signup.invite_sent_at = None
        mock_signup.onboarded_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        mock_update = MagicMock()
        mock_update.model_dump.return_value = {"status": BetaSignupStatus.approved}

        await update_beta_signup(mock_db, 1, mock_update)

        assert mock_signup.invite_sent_at is not None

    @pytest.mark.asyncio
    async def test_update_sets_onboarded_at(self):
        from services.beta_signup_service import update_beta_signup
        from schemas import BetaSignupStatus

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_signup.invite_sent_at = datetime.utcnow()
        mock_signup.onboarded_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        mock_update = MagicMock()
        mock_update.model_dump.return_value = {"status": BetaSignupStatus.onboarded}

        await update_beta_signup(mock_db, 1, mock_update)

        assert mock_signup.onboarded_at is not None


class TestApprovRejectSignup:
    @pytest.mark.asyncio
    async def test_approve_signup(self):
        from services.beta_signup_service import approve_beta_signup

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_signup.invite_sent_at = None
        mock_signup.onboarded_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        result = await approve_beta_signup(mock_db, 1)

        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_signup(self):
        from services.beta_signup_service import reject_beta_signup

        mock_db = AsyncMock()
        mock_signup = MagicMock()
        mock_signup.invite_sent_at = None
        mock_signup.onboarded_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_signup
        mock_db.execute.return_value = mock_result

        result = await reject_beta_signup(mock_db, 1)

        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_not_found(self):
        from services.beta_signup_service import approve_beta_signup

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await approve_beta_signup(mock_db, 999)
        assert result is None


class TestGetBetaSignupStats:
    @pytest.mark.asyncio
    async def test_get_stats(self):
        from services.beta_signup_service import get_beta_signup_stats

        mock_db = AsyncMock()

        mock_total = MagicMock(); mock_total.scalar.return_value = 10
        mock_status = MagicMock(); mock_status.__iter__ = MagicMock(return_value=iter([]))
        mock_source = MagicMock(); mock_source.__iter__ = MagicMock(return_value=iter([]))
        mock_team = MagicMock(); mock_team.__iter__ = MagicMock(return_value=iter([]))
        mock_nps = MagicMock(); mock_nps.scalar.return_value = 8.5

        mock_db.execute.side_effect = [mock_total, mock_status, mock_source, mock_team, mock_nps]

        result = await get_beta_signup_stats(mock_db)

        assert result["total"] == 10
        assert result["average_nps"] == 8.5

    @pytest.mark.asyncio
    async def test_get_stats_zero_total(self):
        from services.beta_signup_service import get_beta_signup_stats

        mock_db = AsyncMock()

        mock_total = MagicMock(); mock_total.scalar.return_value = 0
        mock_status = MagicMock(); mock_status.__iter__ = MagicMock(return_value=iter([]))
        mock_source = MagicMock(); mock_source.__iter__ = MagicMock(return_value=iter([]))
        mock_team = MagicMock(); mock_team.__iter__ = MagicMock(return_value=iter([]))
        mock_nps = MagicMock(); mock_nps.scalar.return_value = None

        mock_db.execute.side_effect = [mock_total, mock_status, mock_source, mock_team, mock_nps]

        result = await get_beta_signup_stats(mock_db)

        assert result["total"] == 0
        assert result["conversion_rate"] == 0.0
        assert result["average_nps"] is None
