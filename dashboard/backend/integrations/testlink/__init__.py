"""
TestLink Integration

Provides integration with TestLink - open source test management tool.
FREE and open source.

Features:
- Test case management
- Test execution tracking
- Requirements traceability
"""

from .client import TestLinkIntegration
from .config import TestLinkConfig

__all__ = ['TestLinkIntegration', 'TestLinkConfig']
