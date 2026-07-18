"""
Authentication Configuration
Alias to main settings
"""
from .settings import settings

# Alias auth_settings to settings for backward compatibility
auth_settings = settings

__all__ = ["auth_settings"]
