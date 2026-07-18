"""Feature flags for phased migration."""

from typing import Optional


class FeatureFlags:
    """Feature flags untuk kontrol migrasi."""
    
    # ===== Legacy Adapter =====
    # True = gunakan legacy adapter (kompatibilitas)
    # False = gunakan new presenter (pure serialization)
    USE_LEGACY_ADAPTER: bool = True
    
    # ===== Deprecation Warning =====
    # True = tampilkan warning di log
    # False = silent
    SHOW_DEPRECATION_WARNING: bool = True
    
    @classmethod
    def disable_legacy_adapter(cls) -> None:
        """Turn off legacy adapter (after all consumers migrated)."""
        cls.USE_LEGACY_ADAPTER = False
    
    @classmethod
    def silence_deprecation_warnings(cls) -> None:
        """Silence deprecation warnings (during contract freeze)."""
        cls.SHOW_DEPRECATION_WARNING = False