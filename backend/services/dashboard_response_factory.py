# ============================================================
# dashboard_response_factory.py
# Sprint 2.2A - Response Factory
#
# Seluruh metadata response dipusatkan di sini sehingga
# DashboardIntelligenceAnalyticsService hanya menjadi orchestrator.
# ============================================================

from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from typing import Any
from typing import Dict

from backend.services.dashboard_snapshot import DashboardSnapshot


class DashboardResponseFactory:
    """
    Factory untuk seluruh response Dashboard Intelligence.

    Tujuan:
        - Konsistensi metadata
        - Service tidak lagi membangun response sendiri
        - Mudah dikembangkan jika metadata bertambah
    """

    ENGINE_NAME = "NEMESIS Intelligence Engine"
    ENGINE_VERSION = "V8+"
    CACHE_VERSION = "2.2"

    # ========================================================
    # AGE FORMATTER
    # ========================================================

    @staticmethod
    def _format_age(age: timedelta) -> str:
        seconds = int(age.total_seconds())

        if seconds < 60:
            return f"{seconds}s ago"

        if seconds < 3600:
            return f"{seconds // 60}m ago"

        if seconds < 86400:
            return f"{seconds // 3600}h ago"

        return f"{seconds // 86400}d ago"

    # ========================================================
    # METADATA
    # ========================================================

    @classmethod
    def build_metadata(
        cls,
        snapshot: DashboardSnapshot,
    ) -> Dict[str, Any]:

        age = datetime.utcnow() - snapshot.generated_at

        metadata = {

            "generated_at":
                snapshot.generated_at.isoformat(),

            "snapshot_id":
                snapshot.snapshot_id,

            "snapshot_version":
                snapshot.snapshot_version,

            "engine":
                cls.ENGINE_NAME,

            "engine_version":
                cls.ENGINE_VERSION,

            "cache_version":
                cls.CACHE_VERSION,

            "status":
                "SUCCESS",

            "entity_count":
                snapshot.entity_count,

            "execution_ms":
                snapshot.execution_ms,

            "cache_hit":
                snapshot.cache_hit,

            "snapshot_age_seconds":
                round(age.total_seconds(), 2),

            "snapshot_age_human":
                cls._format_age(age),

            "collector_metrics":
                snapshot.collector_metrics,

        }

        return metadata

    # ========================================================
    # STANDARD RESPONSE
    # ========================================================

    @classmethod
    def build_response(
        cls,
        snapshot: DashboardSnapshot,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {

            "metadata":
                cls.build_metadata(snapshot),

            "data":
                data,

        }

    # ========================================================
    # ERROR RESPONSE
    # ========================================================

    @classmethod
    def build_error(
        cls,
        snapshot: DashboardSnapshot,
        message: str,
        code: str = "ERROR",
    ) -> Dict[str, Any]:

        metadata = cls.build_metadata(snapshot)

        metadata["status"] = code

        return {

            "metadata":
                metadata,

            "error": {

                "message":
                    message,

                "code":
                    code,

            }

        }

    # ========================================================
    # HEALTH RESPONSE
    # ========================================================

    @classmethod
    def build_health(
        cls,
        snapshot: DashboardSnapshot,
    ) -> Dict[str, Any]:

        return cls.build_response(

            snapshot,

            {

                "engine":
                    cls.ENGINE_NAME,

                "engine_version":
                    cls.ENGINE_VERSION,

                "snapshot_version":
                    snapshot.snapshot_version,

                "snapshot_id":
                    snapshot.snapshot_id,

                "generated_at":
                    snapshot.generated_at.isoformat(),

                "entity_count":
                    snapshot.entity_count,

                "cache_loaded":
                    True,

                "cache_hit":
                    snapshot.cache_hit,

                "execution_ms":
                    snapshot.execution_ms,

            },

        )

    # ========================================================
    # SIMPLE SUCCESS RESPONSE
    # ========================================================

    @classmethod
    def build_success(
        cls,
        snapshot: DashboardSnapshot,
        message: str,
        **extra,
    ) -> Dict[str, Any]:

        payload = {

            "success": True,

            "message": message,

        }

        payload.update(extra)

        return cls.build_response(
            snapshot,
            payload,
        )


# ============================================================
# Singleton
# ============================================================

dashboard_response_factory = DashboardResponseFactory()