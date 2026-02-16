"""
HP ALM / OpenText ALM Integration

Provides integration with HP ALM (now OpenText ALM).
NOTE: This is a PAID enterprise tool - no free tier.

Features:
- Test plan management
- Test lab / executions
- Defects management
- Requirements traceability
"""

from .client import ALMIntegration
from .config import ALMConfig

__all__ = ['ALMIntegration', 'ALMConfig']
