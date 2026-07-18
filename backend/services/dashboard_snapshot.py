# ============================================================
# dashboard_snapshot.py
# Sprint 2.2A - Immutable Dashboard Snapshot
#
# Single Source of Truth untuk seluruh Dashboard Intelligence.
#
# Prinsip:
#   - Immutable (frozen=True)
#   - Memory efficient (slots=True)
#   - O(1) lookup
#   - Tidak mengetahui database
#   - Tidak mengetahui SQLAlchemy
#   - Tidak mengetahui Graph Engine
#
# Snapshot ini hanya berisi hasil collector.
# ============================================================

from __future__ import annotations

import uuid

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# DASHBOARD SNAPSHOT
# ============================================================


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    """
    Immutable Dashboard Snapshot.

    Snapshot adalah hasil collector yang telah lengkap.

    Seluruh endpoint dashboard hanya membaca object ini.

    Tidak boleh dimodifikasi setelah dibuat.
    """

    # --------------------------------------------------------
    # Snapshot Identity
    # --------------------------------------------------------

    snapshot_id: str

    snapshot_version: str

    generated_at: datetime

    # --------------------------------------------------------
    # Entity Storage
    # --------------------------------------------------------

    entity_count: int

    entities: List[Dict[str, Any]] = field(default_factory=list)

    # O(1)
    entity_by_id: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )

    # O(1)
    entity_by_name: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )

    # normalized -> list
    entity_by_normalized: Dict[
        str,
        List[Dict[str, Any]]
    ] = field(default_factory=dict)

    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    analytics: Dict[str, Any] = field(default_factory=dict)

    # --------------------------------------------------------
    # Rankings
    # --------------------------------------------------------

    rankings: Dict[
        str,
        List[Dict[str, Any]]
    ] = field(default_factory=dict)

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    execution_ms: float = 0.0

    cache_hit: bool = False

    collector_metrics: Dict[str, float] = field(
        default_factory=dict
    )

    # ========================================================
    # ENTITY LOOKUP
    # ========================================================

    def get_entity_by_id(
        self,
        entity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        O(1)
        """

        return self.entity_by_id.get(entity_id)

    def get_entity_by_name(
        self,
        entity_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        O(1)
        """

        return self.entity_by_name.get(entity_name)

    def get_entity_by_normalized(
        self,
        entity_name: str,
    ) -> List[Dict[str, Any]]:
        """
        O(1)

        Bisa mengembalikan lebih dari satu entity.
        """

        key = self.normalize_name(entity_name)

        return self.entity_by_normalized.get(key, [])

    # ========================================================
    # ANALYTICS
    # ========================================================

    def get_analytics(
        self,
        section: Optional[str] = None,
    ) -> Any:
        """
        Ambil analytics.

        section=None -> seluruh analytics
        """

        if section is None:
            return self.analytics

        return self.analytics.get(section, {})

    # ========================================================
    # RANKINGS
    # ========================================================

    def get_ranking(
        self,
        ranking_name: str,
    ) -> List[Dict[str, Any]]:

        return self.rankings.get(ranking_name, [])

    def get_top_risk(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        return self.rankings.get(
            "fraud",
            [],
        )[:limit]

    def get_top_confidence(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        return self.rankings.get(
            "confidence",
            [],
        )[:limit]

    def get_top_network(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        return self.rankings.get(
            "network",
            [],
        )[:limit]

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def normalize_name(
        value: Optional[str],
    ) -> str:
        """
        Nama vendor yang dinormalisasi.

        Dipakai untuk lookup.
        """

        if not value:
            return ""

        name = value.upper().strip()

        prefixes = [
            "PT.",
            "PT ",
            "CV.",
            "CV ",
            "UD.",
            "UD ",
        ]

        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]

        return " ".join(name.split())

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_metadata(self) -> Dict[str, Any]:

        return {
            "snapshot_id": self.snapshot_id,
            "snapshot_version": self.snapshot_version,
            "generated_at": self.generated_at.isoformat(),
            "entity_count": self.entity_count,
            "execution_ms": self.execution_ms,
            "cache_hit": self.cache_hit,
        }


# ============================================================
# SNAPSHOT FACTORY
# ============================================================


class SnapshotFactory:
    """
    Factory untuk membuat immutable snapshot.
    """

    SNAPSHOT_VERSION = "2.2A"

    @classmethod
    def create_empty(
        cls,
    ) -> DashboardSnapshot:

        return DashboardSnapshot(
            snapshot_id=str(uuid.uuid4()),
            snapshot_version=cls.SNAPSHOT_VERSION,
            generated_at=datetime.utcnow(),
            entity_count=0,
            entities=[],
            entity_by_id={},
            entity_by_name={},
            entity_by_normalized={},
            analytics={},
            rankings={},
            execution_ms=0.0,
            cache_hit=False,
            collector_metrics={},
        )

    @classmethod
    def create(
        cls,
        *,
        entities: List[Dict[str, Any]],
        analytics: Dict[str, Any],
        rankings: Dict[str, List[Dict[str, Any]]],
        collector_metrics: Dict[str, float],
        execution_ms: float,
        cache_hit: bool = False,
    ) -> DashboardSnapshot:
        """
        Bangun immutable snapshot lengkap.
        """

        entity_by_id: Dict[str, Dict[str, Any]] = {}

        entity_by_name: Dict[str, Dict[str, Any]] = {}

        entity_by_normalized: Dict[
            str,
            List[Dict[str, Any]],
        ] = {}

        for entity in entities:

            entity_id = str(entity.get("id"))

            entity_name = entity.get("name", "")

            entity_by_id[entity_id] = entity

            entity_by_name[entity_name] = entity

            normalized = DashboardSnapshot.normalize_name(
                entity_name
            )

            entity_by_normalized.setdefault(
                normalized,
                [],
            ).append(entity)

        return DashboardSnapshot(
            snapshot_id=str(uuid.uuid4()),
            snapshot_version=cls.SNAPSHOT_VERSION,
            generated_at=datetime.utcnow(),
            entity_count=len(entities),
            entities=entities,
            entity_by_id=entity_by_id,
            entity_by_name=entity_by_name,
            entity_by_normalized=entity_by_normalized,
            analytics=analytics,
            rankings=rankings,
            execution_ms=execution_ms,
            cache_hit=cache_hit,
            collector_metrics=collector_metrics,
        )