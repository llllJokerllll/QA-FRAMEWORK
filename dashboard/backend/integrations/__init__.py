"""
Integration Hub for QA-FRAMEWORK Dashboard

Provides pluggable integrations with external test management systems:
- Jira (Atlassian)
- Zephyr Squad
- HP ALM / OpenText ALM
- TestLink
- Azure DevOps

All integrations follow the IntegrationBase interface for consistency.
"""

from .base import IntegrationBase, IntegrationConfig, TestResult
from .manager import IntegrationManager, integration_manager

__all__ = [
    'IntegrationBase',
    'IntegrationConfig',
    'TestResult',
    'IntegrationManager',
    'integration_manager',
]
