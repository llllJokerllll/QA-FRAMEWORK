from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Multi-tenant
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True)
    
    # OAuth
    oauth_provider = Column(String, nullable=True)
    oauth_provider_id = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    test_executions = relationship("TestExecution", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    hashed_key = Column(String, unique=True, nullable=False)
    scopes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    framework_type = Column(String, default="pytest")  # pytest, unittest, etc.
    config = Column(JSON)  # Configuration parameters
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    tests = relationship("TestCase", back_populates="suite")
    executions = relationship("TestExecution", back_populates="suite")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    test_code = Column(Text, nullable=False)  # The actual test code
    test_type = Column(String, default="api")  # api, ui, db, security, etc.
    priority = Column(String, default="medium")  # low, medium, high, critical
    tags = Column(JSON)  # ["smoke", "regression", "performance"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    suite = relationship("TestSuite", back_populates="tests")
    executions = relationship("TestExecutionDetail", back_populates="test_case")


class TestExecution(Base):
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=False)
    executed_by = Column(Integer, ForeignKey("users.id"))
    execution_type = Column(String, default="manual")  # manual, scheduled, ci
    environment = Column(String, default="production")  # dev, staging, production
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    status = Column(String, default="running")  # running, passed, failed, skipped, error
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    results_summary = Column(JSON)  # Summary of results
    artifacts_path = Column(String)  # Path to artifacts like screenshots, logs

    # Relationships
    suite = relationship("TestSuite", back_populates="executions")
    user = relationship("User", back_populates="test_executions")
    details = relationship("TestExecutionDetail", back_populates="execution")


class TestExecutionDetail(Base):
    __tablename__ = "test_execution_details"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    status = Column(String, default="running")  # passed, failed, skipped, error
    error_message = Column(Text)
    traceback = Column(Text)
    screenshot_path = Column(String)  # Path to screenshot if UI test failed
    logs = Column(Text)  # Execution logs

    # Relationships
    execution = relationship("TestExecution", back_populates="details")
    test_case = relationship("TestCase", back_populates="executions")


class TestArtifact(Base):
    __tablename__ = "test_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    artifact_type = Column(String, nullable=False)  # screenshot, video, log, report
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=func.now())


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=False)
    name = Column(String, nullable=False)
    cron_expression = Column(String, nullable=False)  # Cron expression for scheduling
    is_active = Column(Boolean, default=True)
    next_run = Column(DateTime)
    last_run = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    suite = relationship("TestSuite")
    creator = relationship("User")


class TenantModel(Base):
    """SQLAlchemy model for Tenant entity (multi-tenancy support)"""
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, index=True)  # UUID as string
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    plan = Column(String, nullable=False, default="free")  # free, pro, enterprise
    status = Column(String, nullable=False, default="trial")  # active, suspended, trial
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())