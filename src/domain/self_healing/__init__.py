"""
Self-Healing Tests Domain Module

This module provides the domain layer for AI-powered self-healing tests,
enabling automatic detection and repair of broken selectors.
"""

from .entities import Selector, HealingResult, HealingSession
from .value_objects import SelectorType, HealingStatus, ConfidenceLevel
from .interfaces import ISelectorHealer, ISelectorRepository, IConfidenceScorer

__all__ = [
    # Entities
    "Selector",
    "HealingResult",
    "HealingSession",
    # Value Objects
    "SelectorType",
    "HealingStatus",
    "ConfidenceLevel",
    # Interfaces
    "ISelectorHealer",
    "ISelectorRepository",
    "IConfidenceScorer",
]
