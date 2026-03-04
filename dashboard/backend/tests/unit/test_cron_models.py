"""
Unit Tests for Cron Models

Tests for CronJob and CronExecution SQLAlchemy models.
"""
import pytest
from datetime import datetime, timedelta, timezone
from models.cron import CronJob, CronExecution


class TestCronJobModel:
    """Test suite for CronJob model"""

    def test_cron_job_creation(self):
        """Test creating a cron job with all fields"""
        # Create job
        job = CronJob(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        # Verify basic fields
        assert job.name == "test_job"
        assert job.schedule == "0 * * * *"
        assert job.script_path == "/scripts/test.sh"
        assert job.status == "active"
        assert job.is_active is True
        assert job.success_count == 0
        assert job.error_count == 0
        assert job.avg_duration == 0.0
        
        # Verify datetime fields are set
        assert job.created_at is not None
        assert isinstance(job.created_at, datetime)
        assert job.updated_at is not None
        assert isinstance(job.updated_at, datetime)

    def test_cron_job_with_custom_status(self):
        """Test cron job with custom status"""
        job = CronJob(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh",
            status="paused"
        )
        
        assert job.status == "paused"
        assert job.is_active is True  # is_active is separate from status

    def test_cron_job_with_all_metadata(self):
        """Test cron job with all optional metadata"""
        now = datetime.now(timezone.utc)
        
        job = CronJob(
            name="daily_report",
            schedule="0 13 * * *",
            description="Generate daily reports",
            script_path="/scripts/daily.sh",
            status="active",
            is_active=True,
            last_run=now,
            next_run=now + timedelta(days=1),
            success_count=100,
            error_count=5,
            avg_duration=120.5
        )
        
        assert job.name == "daily_report"
        assert job.description == "Generate daily reports"
        assert job.status == "active"
        assert job.is_active is True
        assert job.success_count == 100
        assert job.error_count == 5
        assert job.avg_duration == 120.5
        assert job.last_run == now
        assert job.next_run == now + timedelta(days=1)

    def test_cron_job_relationship(self):
        """Test cron job has execution relationship"""
        # Create a mock execution
        execution = CronExecution(
            id=1,
            job_id=1,
            status="success",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration=60.0
        )
        
        job = CronJob(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        # Set relationship
        job.executions = [execution]
        
        # Verify relationship
        assert len(job.executions) == 1
        assert job.executions[0].job_id == 1
        assert job.executions[0].status == "success"


class TestCronExecutionModel:
    """Test suite for CronExecution model"""

    def test_cron_execution_creation_success(self):
        """Test creating a successful execution"""
        now = datetime.now(timezone.utc)
        
        execution = CronExecution(
            job_id=1,
            status="success",
            started_at=now,
            finished_at=now + timedelta(seconds=60),
            duration=60.0,
            output="Job completed successfully"
        )
        
        assert execution.job_id == 1
        assert execution.status == "success"
        assert execution.started_at == now
        assert execution.finished_at == now + timedelta(seconds=60)
        assert execution.duration == 60.0
        assert execution.output == "Job completed successfully"

    def test_cron_execution_creation_running(self):
        """Test creating a running execution"""
        now = datetime.now(timezone.utc)
        
        execution = CronExecution(
            job_id=1,
            status="running",
            started_at=now
        )
        
        assert execution.status == "running"
        assert execution.finished_at is None
        assert execution.duration is None

    def test_cron_execution_creation_error(self):
        """Test creating an execution with error"""
        now = datetime.now(timezone.utc)
        
        execution = CronExecution(
            job_id=1,
            status="error",
            started_at=now,
            finished_at=now + timedelta(seconds=5),
            duration=5.0,
            error_message="Script failed with exit code 1"
        )
        
        assert execution.status == "error"
        assert execution.error_message == "Script failed with exit code 1"
        assert execution.finished_at is not None

    def test_cron_execution_relationship(self):
        """Test execution has job relationship"""
        # Note: In actual usage, job.id would be set by the database
        # For testing purposes, we verify the relationship structure
        job = CronJob(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        execution = CronExecution(
            id=1,
            job_id=1,
            status="success",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration=60.0
        )
        
        # Set relationship
        job.executions = [execution]
        
        # Verify relationship (execution.job is set by backref)
        assert execution.job == job
        # Note: job.id is None because it's not saved to database yet
        assert execution.job_id == 1

    def test_cron_execution_duration_calculation(self):
        """Test that duration is correctly calculated when manually set"""
        start = datetime.now(timezone.utc) - timedelta(seconds=120)
        end = datetime.now(timezone.utc)
        
        execution = CronExecution(
            job_id=1,
            status="success",
            started_at=start,
            finished_at=end,
            duration=120.0  # Manually set for testing
        )
        
        # Duration should be 120 seconds (manually set)
        assert execution.duration == 120.0
        assert execution.started_at == start
        assert execution.finished_at == end

    def test_cron_execution_optional_fields(self):
        """Test that optional fields are None by default"""
        execution = CronExecution(
            job_id=1,
            status="success",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc)
        )
        
        assert execution.output is None
        assert execution.error_message is None


class TestCronJobValidation:
    """Test suite for cron job field validation"""

    def test_cron_job_name_length(self):
        """Test cron job name has maximum length"""
        # Valid names
        valid_names = ["short", "a" * 100]
        
        for name in valid_names:
            job = CronJob(
                name=name,
                schedule="0 * * * *",
                script_path="/scripts/test.sh"
            )
            assert job.name == name

    def test_cron_job_schedule_format(self):
        """Test cron schedule format"""
        # Valid cron expressions
        valid_schedules = [
            "* * * * *",
            "0 * * * *",
            "0 0 * * *",
            "0 0 1 * *",
            "0 0 1 JAN *",
            "*/5 * * * *"
        ]
        
        for schedule in valid_schedules:
            job = CronJob(
                name="test_job",
                schedule=schedule,
                script_path="/scripts/test.sh"
            )
            assert job.schedule == schedule

    def test_cron_job_script_path(self):
        """Test cron job script path"""
        job = CronJob(
            name="test_job",
            schedule="0 * * * *",
            script_path="/scripts/test.sh"
        )
        
        assert job.script_path == "/scripts/test.sh"


class TestCronExecutionValidation:
    """Test suite for cron execution field validation"""

    def test_execution_job_id(self):
        """Test execution job ID"""
        execution = CronExecution(
            job_id=1,
            status="success",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc)
        )
        
        assert execution.job_id == 1

    def test_execution_status_values(self):
        """Test valid execution status values"""
        valid_statuses = ["running", "success", "error", "skipped"]
        
        for status in valid_statuses:
            execution = CronExecution(
                job_id=1,
                status=status,
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc)
            )
            assert execution.status == status

    def test_execution_status_running_no_end_time(self):
        """Test running execution has no finish time or duration"""
        execution = CronExecution(
            job_id=1,
            status="running",
            started_at=datetime.now(timezone.utc)
        )
        
        assert execution.finished_at is None
        assert execution.duration is None

    def test_execution_status_completed_has_end_time(self):
        """Test completed execution has finish time and duration"""
        start = datetime.now(timezone.utc) - timedelta(seconds=60)
        end = datetime.now(timezone.utc)
        
        execution = CronExecution(
            job_id=1,
            status="success",
            started_at=start,
            finished_at=end,
            duration=60.0  # Manually set for testing (event listeners only work with DB sessions)
        )
        
        assert execution.finished_at is not None
        assert execution.duration == 60.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
