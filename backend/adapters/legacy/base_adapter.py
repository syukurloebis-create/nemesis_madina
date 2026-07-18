"""Base adapter for legacy compatibility."""

import logging
from backend.mappers.status_mapper import StatusMapper
from backend.config.features import FeatureFlags

logger = logging.getLogger(__name__)


class BaseLegacyAdapter:
    """Base adapter for all legacy adapters."""
    
    @classmethod
    def to_legacy_status(cls, engine_status) -> str:
        """Convert EngineStatus to legacy status string."""
        if FeatureFlags.SHOW_DEPRECATION_WARNING:
            logger.warning(
                "Legacy adapter used: engine_status %s mapped to legacy status",
                engine_status
            )
        return StatusMapper.to_legacy(engine_status)