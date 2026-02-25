"""
AI Test Generation Domain Module

This module provides intelligent test generation capabilities:
- Generate tests from requirements documents
- Generate tests from UI automation analysis
- Generate edge cases automatically
"""

from .value_objects import (
    GenerationType,
    TestFramework,
    TestPriority,
    GenerationStatus,
    ConfidenceLevel,
    RequirementSource,
    TestCaseMetadata,
)
from .entities import (
    GeneratedTest,
    TestScenario,
    EdgeCase,
    TestGenerationSession,
)

__all__ = [
    # Value Objects
    "GenerationType",
    "TestFramework",
    "TestPriority",
    "GenerationStatus",
    "ConfidenceLevel",
    "RequirementSource",
    "TestCaseMetadata",
    # Entities
    "GeneratedTest",
    "TestScenario",
    "EdgeCase",
    "TestGenerationSession",
]
