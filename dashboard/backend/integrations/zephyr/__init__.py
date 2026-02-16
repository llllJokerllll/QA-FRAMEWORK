"""
Zephyr Integration

Provides integration with Zephyr Squad for Jira.
FREE tier: Up to 10 users, unlimited tests

Features:
- Test case management
- Test cycles/executions
- Test results sync
- BDD support
"""

from .client import ZephyrIntegration
from .config import ZephyrConfig

__all__ = ['ZephyrIntegration', 'ZephyrConfig']
