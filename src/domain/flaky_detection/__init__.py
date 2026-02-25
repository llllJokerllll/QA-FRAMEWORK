"""
Flaky Test Detection Domain Module

AI-powered detection and analysis of flaky tests.
"""

from .entities import FlakyTest, FlakyDetectionSession, TestRun, QuarantineEntry
from .value_objects import FlakyStatus, QuarantineReason, DetectionMethod
from .interfaces import IFlakyDetector, IQuarantineManager, ITestRunRepository

__all__ = [
    # Entities
    "FlakyTest",
    "FlakyDetectionSession",
    "TestRun",
    "QuarantineEntry",
    # Value Objects
    "FlakyStatus",
    "QuarantineReason",
    "DetectionMethod",
    # Interfaces
    "IFlakyDetector",
    "IQuarantineManager",
    "ITestRunRepository",
]
