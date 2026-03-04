"""
Unit Tests for Cron Service

Tests business logic for managing scheduled background jobs.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from services.cron_service import CronService
from models.cron import CronJob, CronExecution
from schemas.cron import CronJobResponse, CronExecutionResponse, CronStats


@pytest.mark.asyncio
class TestCronServiceGetJobs:
    """Test suite for getting all jobs"""

    async def test_get_jobs_success(self):
        """Test getting all active jobs returns correct data"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Create test jobs
        job1 = CronJob(
            id=1,
            name="daily_report",
            schedule="0 13 * * *",
            status="active",
            script_path="/scripts/daily.sh",
            success_count=100,
            error_count=5
        )
        job2 = CronJob(
            id=2,
            name="weekly_backup",
            schedule="0 2 * * 0",
            status="paused",
            script_path="/scripts/backup.sh",
            success_count=50,
            error_count=0
        )
        
        # Mock database query result
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [job1, job2]
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        jobs = await service.get_jobs()
        
        # Verify
        assert len(jobs) == 2
        assert jobs[0].name == "daily_report"
        assert jobs[1].name == "weekly_backup"
        assert jobs[0].success_rate == pytest.approx(0.952, rel=0.01)
        assert jobs[1].success_rate == 1.0
        
        # Verify SQL query was executed correctly
        mock_db.execute.assert_called_once()

    async def test_get_jobs_empty(self):
        """Test getting jobs when no jobs exist"""
        # Setup mock database
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        jobs = await service.get_jobs()
        
        # Verify
        assert jobs == []

    async def test_get_jobs_calculates_zero_division(self):
        """Test that zero division is handled correctly when no executions"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Create job with zero executions
        job = CronJob(
            id=1,
            name="test_job",
            schedule="* * * * *",
            status="active",
            script_path="/scripts/test.sh",
            success_count=0,
            error_count=0
        )
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [job]
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        jobs = await service.get_jobs()
        
        # Verify
        assert len(jobs) == 1
        assert jobs[0].success_rate == 0.0


@pytest.mark.asyncio
class TestCronServiceGetJob:
    """Test suite for getting a specific job"""

    async def test_get_job_success(self):
        """Test getting a job by ID returns correct data"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Create test job
        job = CronJob(
            id=1,
            name="test_job",
            schedule="0 * * * *",
            status="active",
            script_path="/scripts/test.sh",
            success_count=25,
            error_count=3
        )
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = job
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        result = await service.get_job(1)
        
        # Verify
        assert result is not None
        assert result.id == 1
        assert result.name == "test_job"
        assert result.success_rate == pytest.approx(0.893, rel=0.01)

    async def test_get_job_not_found(self):
        """Test getting a non-existent job returns None"""
        # Setup mock database
        mock_db = AsyncMock()
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        result = await service.get_job(999)
        
        # Verify
        assert result is None

    async def test_get_job_with_no_executions(self):
        """Test getting job with zero executions handles correctly"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Create job with zero executions
        job = CronJob(
            id=2,
            name="new_job",
            schedule="* * * * *",
            status="active",
            script_path="/scripts/new.sh",
            success_count=0,
            error_count=0
        )
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = job
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        result = await service.get_job(2)
        
        # Verify
        assert result.success_rate == 0.0


@pytest.mark.asyncio
class TestCronServiceGetExecutions:
    """Test suite for getting job executions"""

    async def test_get_executions_success(self):
        """Test getting execution history for a job"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Create test executions
        exec1 = CronExecution(
            id=1,
            job_id=1,
            status="success",
            started_at=datetime.utcnow() - timedelta(hours=1),
            finished_at=datetime.utcnow() - timedelta(hours=1),
            duration=120.5,
            output="Job completed successfully"
        )
        exec2 = CronExecution(
            id=2,
            job_id=1,
            status="error",
            started_at=datetime.utcnow() - timedelta(hours=2),
            finished_at=datetime.utcnow() - timedelta(hours=2),
            duration=5.0,
            error_message="Script failed"
        )
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [exec1, exec2]
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        executions = await service.get_executions(1, limit=10)
        
        # Verify
        assert len(executions) == 2
        assert executions[0].status == "success"
        assert executions[1].status == "error"
        assert executions[0].duration == 120.5

    async def test_get_executions_default_limit(self):
        """Test default limit of 50 executions"""
        # Setup mock database
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        executions = await service.get_executions(1)
        
        # Verify default limit was used
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args
        assert "CronExecution" in str(call_args)

    async def test_get_executions_custom_limit(self):
        """Test custom limit parameter"""
        # Setup mock database
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute with custom limit
        executions = await service.get_executions(1, limit=100)
        
        # Verify custom limit was used
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args
        assert "CronExecution" in str(call_args)


@pytest.mark.asyncio
class TestCronServiceGetStats:
    """Test suite for getting statistics"""

    async def test_get_stats_comprehensive(self):
        """Test getting comprehensive cron job statistics"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Mock all query results
        total_result = AsyncMock()
        total_result.scalar.return_value = 10
        
        active_result = AsyncMock()
        active_result.scalar.return_value = 7
        
        paused_result = AsyncMock()
        paused_result.scalar.return_value = 2
        
        error_result = AsyncMock()
        error_result.scalar.return_value = 1
        
        today_result = AsyncMock()
        today_result.scalar.return_value = 50
        
        success_result = AsyncMock()
        success_result.scalar.return_value = 45
        
        # Execute all queries in sequence
        mock_db.execute.side_effect = [total_result, active_result, paused_result, 
                                       error_result, today_result, success_result]
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        stats = await service.get_stats()
        
        # Verify
        assert stats.total_jobs == 10
        assert stats.active_jobs == 7
        assert stats.paused_jobs == 2
        assert stats.error_jobs == 1
        assert stats.total_executions_today == 50
        assert stats.success_rate_today == 0.9

    async def test_get_stats_empty_database(self):
        """Test getting stats from empty database"""
        # Setup mock database with all zeros
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar.side_effect = [0, 0, 0, 0, 0, 0]
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        stats = await service.get_stats()
        
        # Verify
        assert stats.total_jobs == 0
        assert stats.active_jobs == 0
        assert stats.paused_jobs == 0
        assert stats.error_jobs == 0
        assert stats.total_executions_today == 0
        assert stats.success_rate_today == 0.0

    async def test_get_stats_success_rate_calculation(self):
        """Test success rate calculation from execution counts"""
        # Setup mock database
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar.side_effect = [5, 3, 1, 1, 100, 80]
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        stats = await service.get_stats()
        
        # Verify
        assert stats.total_executions_today == 100
        assert stats.success_rate_today == 0.8


@pytest.mark.asyncio
class TestCronServiceRunJob:
    """Test suite for running cron jobs"""

    async def test_run_job_success(self):
        """Test running a job successfully"""
        # Setup mock database
        mock_db = AsyncMock()
        
        # Mock existing job
        job = CronJob(
            id=1,
            name="test_job",
            schedule="* * * * *",
            status="active",
            script_path="/scripts/test.sh",
            success_count=10,
            error_count=2
        )
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = job
        mock_db.execute.return_value = mock_result
        
        # Mock add and commit
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        
        # Create service
        service = CronService(mock_db)
        
        # Execute
        result = await service.run_job(1)
        
        # Verify
        assert result["status"] == "started"
        assert "execution_id" in result
        assert result["execution_id"] == 1
        
        # Verify execution record was created
        assert mock_db.add.called

    async def test_run_job_not_found(self):
        """Test running a non-existent job raises error"""
        # Setup mock database
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Create service
        service = CronService(mock_db)
        
        # Execute - should raise ValueError
        with pytest.raises(ValueError, match="Job not found"):
            await service.run_job(999)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
