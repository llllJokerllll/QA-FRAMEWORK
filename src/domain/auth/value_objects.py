"""OAuth Value Objects."""
from enum import Enum
from typing import Optional


class AuthProvider(Enum):
    """Enumeration of supported authentication providers."""
    GOOGLE = "google"
    GITHUB = "github"
    EMAIL = "email"
    
    @classmethod
    def from_string(cls, value: str) -> Optional["AuthProvider"]:
        """Create AuthProvider from string value (case-insensitive)."""
        try:
            return cls(value.lower())
        except ValueError:
            return None
    
    @property
    def display_name(self) -> str:
        """Human-readable provider name."""
        return self.value.title()
    
    def __str__(self) -> str:
        return self.value