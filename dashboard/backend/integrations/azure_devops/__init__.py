"""
Azure DevOps Integration

Provides integration with Microsoft Azure DevOps.
FREE tier: Up to 5 users.

Features:
- Work items (user stories, tasks, bugs)
- Test plans and test suites
- Test results
- CI/CD integration
"""

from .client import AzureDevOpsIntegration
from .config import AzureDevOpsConfig

__all__ = ['AzureDevOpsIntegration', 'AzureDevOpsConfig']
