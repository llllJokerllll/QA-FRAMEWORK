"""Value objects for authentication domain."""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


class AuthProvider(str, Enum):
    """Supported authentication providers."""
    
    GOOGLE = "google"
    GITHUB = "github"
    EMAIL = "email"
    API_KEY = "api_key"


class TokenStatus(str, Enum):
    """Token lifecycle status."""
    
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    USED = "used"


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""
    
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with strength validation."""
    
    hashed_value: str
    
    @staticmethod
    def validate_strength(password: str) -> tuple[bool, list[str]]:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        - At least 1 special character
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least 1 uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least 1 lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least 1 number")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least 1 special character")
        
        return len(errors) == 0, errors


@dataclass(frozen=True)
class OAuthState:
    """OAuth state parameter for CSRF protection."""
    
    value: str
    created_at: datetime
    provider: AuthProvider
    redirect_uri: Optional[str] = None
    
    def is_expired(self, max_age_seconds: int = 600) -> bool:
        """Check if state has expired (default 10 minutes)."""
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age > max_age_seconds


@dataclass(frozen=True)
class Scope:
    """OAuth scope value object."""
    
    permissions: frozenset[str]
    
    @classmethod
    def from_string(cls, scope_string: str) -> "Scope":
        """Create Scope from space-separated string."""
        permissions = frozenset(scope_string.split())
        return cls(permissions=permissions)
    
    def to_string(self) -> str:
        """Convert to space-separated string."""
        return " ".join(sorted(self.permissions))
    
    def has_permission(self, permission: str) -> bool:
        """Check if scope includes a permission."""
        return permission in self.permissions
    
    def __or__(self, other: "Scope") -> "Scope":
        """Combine two scopes."""
        return Scope(permissions=self.permissions | other.permissions)
    
    def __and__(self, other: "Scope") -> "Scope":
        """Intersect two scopes."""
        return Scope(permissions=self.permissions & other.permissions)
