"""
Jira Integration

Provides integration with Atlassian Jira Cloud and Server.
FREE tier: Up to 10 users

Features:
- Sync test results as issues
- Create bugs from failed tests
- Link test cases to stories/epics
- Bi-directional sync
"""

from .client import JiraIntegration
from .config import JiraConfig

__all__ = ['JiraIntegration', 'JiraConfig']
