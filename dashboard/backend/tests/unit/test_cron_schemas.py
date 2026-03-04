"""
Unit Tests for Cron Schemas

Tests for Pydantic schemas related to cron jobs.
"""
import pytest
from datetime import datetime, timedelta
from schemas.cron import (
    CronJobBase, CronJobCreate, CronJobResponse, CronJobStatus,
    CronExecutionBase, CronExecutionResponse, CronExecutionStatus,
    CronStats
)


class TestCronJobBase:
    """Test suite for CronJobBase schema"""

    def test_cron_job_base_with_minimal_fields(self):
        """Test creating CronJobBase with minimal fields"""
        job_data = CronJobBase(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        assert job_data.name == "test_job"
        assert job_data.schedule == "0 * * * *"
        assert job_data.script_path == "/scripts/test.sh"
        assert job_data.description is None

    def test_cron_job_base_with_description(self):
        """Test creating CronJobBase with description"""
        job_data = CronJobBase(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh",
            description="This is a test job"
        )
        
        assert job_data.description == "This is a test job"

    def test_cron_job_base_validation_min_length(self):
        """Test name validation with minimum length"""
        with pytest.raises(Exception):  # Pydantic validation error
            CronJobBase(
                name="",
                schedule="0 * * * *",
                script_path="/scripts/test.sh"
            )

    def test_cron_job_base_validation_max_length(self):
        """Test name validation with maximum length"""
        # This should pass (max 100 chars)
        job_data = CronJobBase(
            name="a" * 100,
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        assert len(job_data.name) == 100

    def test_cron_job_base_validation_invalid_schedule(self):
        """Test schedule validation"""
        # Invalid schedule should raise validation error
        with pytest.raises(Exception):
            CronJobBase(
                name="test_job",
                schedule="invalid_schedule",
                script_path="/scripts/test.sh"
            )

    def test_cron_job_base_script_path_required(self):
        """Test that script path is required"""
        with pytest.raises(Exception):
            CronJobBase(
                name="test_job",
                schedule="0 * * * *",
                script_path=None
            )


class TestCronJobCreate:
    """Test suite for CronJobCreate schema"""

    def test_cron_job_create_basic(self):
        """Test creating CronJobCreate"""
        job_data = CronJobCreate(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        assert job_data.name == "test_job"
        assert job_data.schedule == "0 * * * *"
        assert job_data.script_path == "/scripts/test.sh"

    def test_cron_job_create_complete(self):
        """Test creating CronJobCreate with all fields"""
        job_data = CronJobCreate(
            name="daily_report",
            schedule="0 13 * * *",
            description="Generate daily reports",
            script_path="/scripts/daily.sh"
        )
        
        assert job_data.name == "daily_report"
        assert job_data.schedule == "0 13 * * *"
        assert job_data.description == "Generate daily reports"
        assert job_data.script_path == "/scripts/daily.sh"


class TestCronJobResponse:
    """Test suite for CronJobResponse schema"""

    def test_cron_job_response_from_job_data(self):
        """Test creating CronJobResponse from job data"""
        now = datetime.utcnow()
        
        job_data = CronJobBase(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        response = CronJobResponse(
            id=1,
            name="test_job",
            schedule="0 * * * *",
            status=CronJobStatus.active,
            last_run=now,
            next_run=now + timedelta(hours=1),
            success_rate=0.95,
            avg_duration=60.0,
            is_active=True,
            created_at=now
        )
        
        assert response.id == 1
        assert response.name == "test_job"
        assert response.schedule == "0 * * * *"
        assert response.status == CronJobStatus.active
        assert response.success_rate == 0.95
        assert response.avg_duration == 60.0
        assert response.is_active is True
        assert response.created_at == now

    def test_cron_job_response_from_dict(self):
        """Test creating CronJobResponse from dictionary"""
        response_data = {
            "id": 2,
            "name": "weekly_job",
            "schedule": "0 2 * * 0",
            "status": "active",
            "last_run": None,
            "next_run": None,
            "success_rate": 0.98,
            "avg_duration": 300.0,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        response = CronJobResponse(**response_data)
        
        assert response.id == 2
        assert response.name == "weekly_job"
        assert response.success_rate == 0.98
        assert response.avg_duration == 300.0
        assert response.last_run is None


class TestCronExecutionBase:
    """Test suite for CronExecutionBase schema"""

    def test_cron_execution_base_success(self):
        """Test creating CronExecutionBase for successful execution"""
        now = datetime.utcnow()
        
        exec_data = CronExecutionBase(
            job_id=1,
            status="success",
            started_at=now,
            duration=60.0,
            output="Job completed successfully"
        )
        
        assert exec_data.job_id == 1
        assert exec_data.status == "success"
        assert exec_data.started_at == now
        assert exec_data.duration == 60.0
        assert exec_data.output == "Job completed successfully"

    def test_cron_execution_base_running(self):
        """Test creating CronExecutionBase for running execution"""
        now = datetime.utcnow()
        
        exec_data = CronExecutionBase(
            job_id=1,
            status="running",
            started_at=now
        )
        
        assert exec_data.status == "running"
        assert exec_data.duration is None
        assert exec_data.output is None

    def test_cron_execution_base_error(self):
        """Test creating CronExecutionBase for error execution"""
        now = datetime.utcnow()
        
        exec_data = CronExecutionBase(
            job_id=1,
            status="error",
            started_at=now,
            duration=5.0,
            error_message="Script failed"
        )
        
        assert exec_data.status == "error"
        assert exec_data.error_message == "Script failed"


class TestCronExecutionResponse:
    """Test suite for CronExecutionResponse schema"""

    def test_cron_execution_response_basic(self):
        """Test creating CronExecutionResponse"""
        now = datetime.utcnow()
        end_time = now + timedelta(seconds=60)
        
        exec_data = CronExecutionBase(
            job_id=1,
            status="success",
            started_at=now,
            finished_at=end_time,
            duration=60.0
        )
        
        response = CronExecutionResponse(
            id=1,
            job_id=1,
            status="success",
            started_at=now,
            duration=60.0,
            finished_at=end_time,
            error_message=None,
            created_at=now
        )
        
        assert response.id == 1
        assert response.job_id == 1
        assert response.status == "success"
        assert response.started_at == now
        assert response.duration == 60.0
        assert response.finished_at == end_time
        assert response.error_message is None


class TestCronStats:
    """Test suite for CronStats schema"""

    def test_cron_stats_comprehensive(self):
        """Test creating CronStats with all fields"""
        stats = CronStats(
            total_jobs=10,
            active_jobs=7,
            paused_jobs=2,
            error_jobs=1,
            total_executions_today=50,
            success_rate_today=0.8
        )
        
        assert stats.total_jobs == 10
        assert stats.active_jobs == 7
        assert stats.paused_jobs == 2
        assert stats.error_jobs == 1
        assert stats.total_executions_today == 50
        assert stats.success_rate_today == 0.8

    def test_cron_stats_default_values(self):
        """Test CronStats with default values"""
        stats = CronStats(
            total_jobs=0,
            active_jobs=0,
            paused_jobs=0,
            error_jobs=0,
            total_executions_today=0,
            success_rate_today=0.0
        )
        
        assert stats.total_jobs == 0
        assert stats.success_rate_today == 0.0


class TestCronStatusEnum:
    """Test suite for CronJobStatus enum"""

    def test_cron_job_status_values(self):
        """Test that all status values are valid"""
        assert CronJobStatus.active == "active"
        assert CronJobStatus.paused == "paused"
        assert CronJobStatus.error == "error"

    def test_cron_job_status_is_str_enum(self):
        """Test that status is a string enum"""
        status = CronJobStatus.active
        assert isinstance(status.value, str)
        assert status.value == "active"


class TestCronExecutionStatusEnum:
    """Test suite for CronExecutionStatus enum"""

    def test_cron_execution_status_values(self):
        """Test that all status values are valid"""
        assert CronExecutionStatus.running == "running"
        assert CronExecutionStatus.success == "success"
        assert CronExecutionStatus.error == "error"
        assert CronExecutionStatus.skipped == "skipped"

    def test_cron_execution_status_is_str_enum(self):
        """Test that status is a string enum"""
        status = CronExecutionStatus.success
        assert isinstance(status.value, str)
        assert status.value == "success"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
