"""
Unit tests for cron_service.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCronServiceGetJobs:
    @pytest.mark.asyncio
    async def test_get_jobs_empty(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = CronService(mock_db)
        result = await service.get_jobs()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_jobs_success_rate_80_percent(self):
        """Verify success_rate is 0.8 for 8 success / 2 errors."""
        from services.cron_service import CronService

        mock_db = AsyncMock()
        job = MagicMock()
        job.success_count = 8
        job.error_count = 2

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [job]
        mock_db.execute.return_value = mock_result

        captured = {}

        def capture_response(**kwargs):
            captured.update(kwargs)
            return MagicMock()

        service = CronService(mock_db)
        with patch("services.cron_service.CronJobResponse", side_effect=capture_response):
            await service.get_jobs()

        assert captured["success_rate"] == pytest.approx(0.8)

    @pytest.mark.asyncio
    async def test_get_jobs_zero_executions(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        job = MagicMock()
        job.success_count = 0
        job.error_count = 0

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [job]
        mock_db.execute.return_value = mock_result

        captured = {}

        def capture_response(**kwargs):
            captured.update(kwargs)
            return MagicMock()

        service = CronService(mock_db)
        with patch("services.cron_service.CronJobResponse", side_effect=capture_response):
            await service.get_jobs()

        assert captured["success_rate"] == 0.0


class TestCronServiceGetJob:
    @pytest.mark.asyncio
    async def test_get_job_not_found(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = CronService(mock_db)
        result = await service.get_job(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_job_75_percent_success_rate(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        job = MagicMock()
        job.success_count = 3
        job.error_count = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = job
        mock_db.execute.return_value = mock_result

        captured = {}

        def capture(**kwargs):
            captured.update(kwargs)
            return MagicMock()

        service = CronService(mock_db)
        with patch("services.cron_service.CronJobResponse", side_effect=capture):
            result = await service.get_job(1)

        assert result is not None
        assert captured["success_rate"] == pytest.approx(0.75)

    @pytest.mark.asyncio
    async def test_get_job_zero_executions(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        job = MagicMock()
        job.success_count = 0
        job.error_count = 0

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = job
        mock_db.execute.return_value = mock_result

        captured = {}

        def capture(**kwargs):
            captured.update(kwargs)
            return MagicMock()

        service = CronService(mock_db)
        with patch("services.cron_service.CronJobResponse", side_effect=capture):
            await service.get_job(1)

        assert captured["success_rate"] == 0.0


class TestCronServiceGetExecutions:
    @pytest.mark.asyncio
    async def test_get_executions(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        executions = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = executions
        mock_db.execute.return_value = mock_result

        service = CronService(mock_db)
        result = await service.get_executions(job_id=1)
        assert result == executions

    @pytest.mark.asyncio
    async def test_get_executions_empty(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = CronService(mock_db)
        result = await service.get_executions(job_id=1, limit=5)
        assert result == []


class TestCronServiceGetStats:
    def _make_db(self, total=10, active=7, paused=2, errors=1, today=50, success=45):
        mock_db = AsyncMock()
        def ms(v): m = MagicMock(); m.scalar.return_value = v; return m
        mock_db.execute.side_effect = [ms(total), ms(active), ms(paused), ms(errors), ms(today), ms(success)]
        return mock_db

    @pytest.mark.asyncio
    async def test_stats_values(self):
        from services.cron_service import CronService
        service = CronService(self._make_db())

        with patch("services.cron_service.CronStats") as MockStats:
            MockStats.return_value = MagicMock()
            await service.get_stats()

        kwargs = MockStats.call_args[1]
        assert kwargs["total_jobs"] == 10
        assert kwargs["active_jobs"] == 7
        assert kwargs["success_rate_today"] == pytest.approx(0.9)

    @pytest.mark.asyncio
    async def test_stats_zero_executions_today(self):
        from services.cron_service import CronService
        service = CronService(self._make_db(today=0, success=0))

        with patch("services.cron_service.CronStats") as MockStats:
            MockStats.return_value = MagicMock()
            await service.get_stats()

        kwargs = MockStats.call_args[1]
        assert kwargs["success_rate_today"] == 0.0


class TestCronServiceRunJob:
    @pytest.mark.asyncio
    async def test_run_job_not_found(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        service = CronService(mock_db)
        with patch.object(service, "get_job", return_value=None):
            with pytest.raises(ValueError, match="Job not found"):
                await service.run_job(999)

    @pytest.mark.asyncio
    async def test_run_job_success(self):
        from services.cron_service import CronService

        mock_db = AsyncMock()
        service = CronService(mock_db)

        fake_job = MagicMock(); fake_job.id = 1
        fake_exec = MagicMock(); fake_exec.id = 42

        with patch.object(service, "get_job", return_value=fake_job), \
             patch("services.cron_service.CronExecution", return_value=fake_exec), \
             patch("asyncio.sleep", new_callable=AsyncMock):

            result = await service.run_job(1)

        assert result["status"] == "started"
        assert result["execution_id"] == 42
        mock_db.add.assert_called_once_with(fake_exec)
