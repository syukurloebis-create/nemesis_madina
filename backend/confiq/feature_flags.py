"""
NEMESIS Madina - Feature Flags
✅ Granular rollout flags
"""

import os


class FeatureFlags:
    """Feature flags for gradual rollout."""
    
    # Domain UoW migration by module
    USE_DOMAIN_UOW_DASHBOARD = os.getenv("USE_DOMAIN_UOW_DASHBOARD", "False").lower() == "true"
    USE_DOMAIN_UOW_GRAPH = os.getenv("USE_DOMAIN_UOW_GRAPH", "False").lower() == "true"
    USE_DOMAIN_UOW_RISK = os.getenv("USE_DOMAIN_UOW_RISK", "False").lower() == "true"
    
    # Outbox flags
    USE_MEMORY_OUTBOX = os.getenv("USE_MEMORY_OUTBOX", "False").lower() == "true"
    USE_SQL_OUTBOX = os.getenv("USE_SQL_OUTBOX", "False").lower() == "true"
    
    # Event Bus flags
    USE_NEW_EVENT_BUS = os.getenv("USE_NEW_EVENT_BUS", "False").lower() == "true"