"""
Billing Domain Interfaces

Abstract interfaces for external payment gateways.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from .entities import Plan, Subscription, CheckoutSession
from .value_objects import BillingPeriod, Money


class PaymentGateway(ABC):
    """
    Abstract interface for payment gateways.
    
    This interface defines the contract that any payment gateway
    implementation (Stripe, PayPal, etc.) must fulfill.
    
    Implementations handle external payment provider communication
    while the domain remains provider-agnostic.
    """
    
    @abstractmethod
    async def create_customer(
        self,
        tenant_id: UUID,
        user_id: UUID,
        email: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
