# ============================================================
# dashboard_intelligence_analytics_service.py
# SPRINT 2 - PERFORMANCE ENGINE
# Refactor V2 + Parallel Collector + TTL Cache + Performance Metadata
# ============================================================

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from backend.services.entity_graph_intelligence_service import (
    entity_graph_intelligence_service,
)

from backend.services.dashboard_response_factory import (
    dashboard_response_factory,
)

from backend.services.dashboard_snapshot_builder import (
    dashboard_snapshot_builder,
)

from backend.services.dashboard_snapshot import (
    DashboardSnapshot,
)

from backend.services.dashboard_snapshot import DashboardSnapshot


class DashboardIntelligenceAnalyticsService:

    ENGINE_NAME = "NEMESIS Intelligence Engine"
    ENGINE_VERSION = "V8+"
    CACHE_VERSION = "2.1"

    # TTL Cache - 5 menit default
    CACHE_TTL_SECONDS = 300
    MAX_CONCURRENT_SNAPSHOTS = 10

    def __init__(self):
        # Entity intelligence cache (per-entity)
        self.entity_cache: Dict[str, Dict] = {}

        # Dashboard snapshot cache (aggregated)
        self.snapshot_cache: Optional[DashboardSnapshot] = None
        self.snapshot_timestamp: Optional[datetime] = None

        # Statistics cache (shared)
        self.statistics_cache: Optional[Dict[str, Any]] = None
        self.statistics_timestamp: Optional[datetime] = None

        # Cache lock untuk thread-safety
        self._cache_lock = asyncio.Lock()

    # ============================================================
    # 1. CACHE MANAGEMENT
    # ============================================================

    def clear_cache(self) -> None:
        """Clear all caches"""
        self.entity_cache.clear()
        self.snapshot_cache = None
        self.snapshot_timestamp = None
        self.statistics_cache = None
        self.statistics_timestamp = None

    def _is_cache_valid(self, timestamp: Optional[datetime]) -> bool:
        """Check if cache is still valid based on TTL"""
        if timestamp is None:
            return False

        age = datetime.utcnow() - timestamp
        return age.total_seconds() < self.CACHE_TTL_SECONDS

    def _get_snapshot_age(self) -> Optional[str]:
        """Get human-readable snapshot age"""
        if self.snapshot_timestamp is None:
            return None

        age = datetime.utcnow() - self.snapshot_timestamp
        seconds = age.total_seconds()

        if seconds < 60:
            return f"{int(seconds)}s ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"


    # ============================================================
    # 3. HELPERS
    # ============================================================

    def _safe_float(self, value) -> float:
        try:
            return round(float(value), 2)
        except Exception:
            return 0.0

    def _safe_int(self, value) -> int:
        try:
            return int(value)
        except Exception:
            return 0

    def _normalize_risk(self, score: float) -> str:
        if score >= 85:
            return "CRITICAL"
        if score >= 65:
            return "HIGH"
        if score >= 35:
            return "MEDIUM"
        return "LOW"

    # ============================================================
    # 4. LOAD ENTITY MASTER
    # ============================================================

    async def _load_vendor_entities(self, db) -> List[Dict]:
        """Load all vendor entities from database"""
        result = await db.execute(
            text("""
                SELECT
                    id,
                    name,
                    entity_type
                FROM graph_entities
                WHERE entity_type = 'vendor'
                ORDER BY id
            """)
        )
        return list(result.mappings().all())

    # ============================================================
    # 5. SINGLE ENTITY SNAPSHOT
    # ============================================================

    async def _get_entity_snapshot(
        self,
        entity_name: str,
        db,
    ) -> Dict[str, Any]:
        """
        Get intelligence snapshot for a single entity
        Uses entity_cache for performance
        """
        if entity_name in self.entity_cache:
            return self.entity_cache[entity_name]

        graph = await entity_graph_intelligence_service.get_entity_network(
            entity_name,
            db
        )

        intelligence = graph.get("intelligence", {})

        snapshot = {
            "name": entity_name,
            "fraud_score": self._safe_float(
                intelligence.get("fraud_score", 0)
            ),
            "risk_level": intelligence.get("risk_level", "LOW"),
            "confidence": self._safe_float(
                intelligence.get("confidence", 0)
            ),
            "evidence_grade": intelligence.get("evidence_grade", "UNKNOWN"),
            "intelligence_type": intelligence.get("intelligence_type", "UNKNOWN"),
            "patterns": graph.get("patterns", []),
            "risk_explanation": intelligence.get("risk_explanation", []),
            "score_breakdown": intelligence.get("score_explanation", {}),
            "relationship_metrics": intelligence.get("relationship_metrics", {}),
            "evidence": intelligence.get("evidence", [])
        }

        self.entity_cache[entity_name] = snapshot
        return snapshot


    # ============================================================
    # SPRINT 2.2B
    # MASTER COLLECTOR
    # Menghasilkan DashboardSnapshot
    # ============================================================

    async def _collect_all_snapshots(
        self,
        db,
        refresh: bool = False,
    ):
        """
        Master Collector.

        Seluruh dashboard membaca DashboardSnapshot.

        Flow

            Database
                │
                ▼
          Vendor Entities
                │
                ▼
          Graph Intelligence
                │
                ▼
            Entity List
                │
                ▼
          Snapshot Builder
                │
                ▼
          DashboardSnapshot
        """

        async with self._cache_lock:

            #
            # Return cache
            #

            if (
                not refresh
                and self.snapshot_cache is not None
                and self._is_cache_valid(self.snapshot_timestamp)
            ):

                if not self.snapshot_cache.cache_hit:

                    #
                    # Snapshot immutable
                    # build snapshot baru dengan cache_hit=True
                    #

                    cached_snapshot = dashboard_snapshot_builder.build(
                        entities=self.snapshot_cache.entities,
                        collector_metrics=self.snapshot_cache.collector_metrics,
                        execution_ms=self.snapshot_cache.execution_ms,
                        cache_hit=True,
                    )

                    self.snapshot_cache = cached_snapshot

                return self.snapshot_cache

            #
            # PERFORMANCE TIMER
            #

            total_start = time.perf_counter()

            #
            # STEP 1
            # Load Vendor
            #

            t0 = time.perf_counter()

            vendors = await self._load_vendor_entities(db)

            load_entities_ms = (
                time.perf_counter() - t0
            ) * 1000

            #
            # STEP 2
            # Graph Intelligence
            #

            semaphore = asyncio.Semaphore(
                self.MAX_CONCURRENT_SNAPSHOTS
            )

            async def collect_entity(entity):

                async with semaphore:

                    intelligence = await self._get_entity_snapshot(
                        entity["name"],
                        db,
                    )

                    return {
                        "id": entity["id"],
                        "name": entity["name"],
                        "entity_type": entity["entity_type"],
                        **intelligence,
                    }

            t0 = time.perf_counter()

            entity_list = await asyncio.gather(
                *[
                    collect_entity(entity)
                    for entity in vendors
                ]
            )

            graph_ms = (
                time.perf_counter() - t0
            ) * 1000

            #
            # STEP 3
            # Snapshot Builder
            #

            t0 = time.perf_counter()

            #
            # analytics + ranking
            # dihitung sekali
            #

            execution_ms = (
                time.perf_counter() - total_start
            ) * 1000

            analytics_ms = (
                time.perf_counter() - t0
            ) * 1000

            ranking_ms = 0.0

            collector_metrics = (
                dashboard_snapshot_builder.create_collector_metrics(
                    load_entities_ms=load_entities_ms,
                    graph_ms=graph_ms,
                    analytics_ms=analytics_ms,
                    ranking_ms=ranking_ms,
                    total_ms=execution_ms,
                )
            )

            snapshot = dashboard_snapshot_builder.build(
                entities=entity_list,
                collector_metrics=collector_metrics,
                execution_ms=execution_ms,
                cache_hit=False,
            )

            #
            # STEP 4
            # Copy-On-Write Cache
            #

            self.snapshot_cache = snapshot

            self.snapshot_timestamp = datetime.utcnow()

            return snapshot

    # ============================================================
    # 9. PUBLIC ENDPOINTS
    # ============================================================

    # 9.1 - DASHBOARD SUMMARY

    async def get_dashboard_summary(self, db):

        snapshot = await self._collect_all_snapshots(db)
        
        data = {

            "total_entities":
                snapshot.entity_count,

            "risk_distribution":
                snapshot.analytics["risk"]["distribution"],

            "critical_entities":
                snapshot.analytics["risk"]["critical_count"],

            "high_risk_entities":
                snapshot.analytics["risk"]["high_count"],

            "average_confidence":
                snapshot.analytics["evidence"]["average_confidence"],

            "average_fraud_score":
                snapshot.analytics["evidence"]["average_fraud_score"],

            "fraud_landscape":
                snapshot.analytics["risk"]["landscape"],

            "intelligence_distribution":
                snapshot.analytics["intelligence"]["distribution"],

            "evidence_distribution":
                snapshot.analytics["evidence"]["distribution"],

            "system_status": {

                "status":
                    "ONLINE",

                "engine":
                    self.ENGINE_NAME,

                "version":
                    self.ENGINE_VERSION,

            }

        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.2 - DASHBOARD OVERVIEW

    async def get_overview(self, db):

        snapshot = await self._collect_all_snapshots(db)
        
        risk = snapshot.analytics["risk"]

        evidence = snapshot.analytics["evidence"]

        data = {

            "overview": {

                "headline":
                    "Fraud Intelligence Monitoring Active",

                "risk_level":
                    (
                        "CRITICAL"
                        if risk["critical_count"] > 0
                        else "NORMAL"
                    ),

                "entities_monitored":
                    snapshot.entity_count,

                "average_confidence":
                    evidence["average_confidence"],

            },

            "risk_landscape":
                risk["landscape"],

            "top_entities":
                snapshot.get_top_risk(5),

            "ai_engine": {

                "name":
                    self.ENGINE_NAME,

                "status":
                    "ONLINE",

                "version":
                    self.ENGINE_VERSION,

            }

        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.3 - DASHBOARD KPI

    async def get_dashboard_kpi(self, db):

        snapshot = await self._collect_all_snapshots(db)

        risk = snapshot.analytics["risk"]

        evidence = snapshot.analytics["evidence"]

        data = {

            "total_entities":
                snapshot.entity_count,

            "critical_count":
                risk["critical_count"],

            "high_count":
                risk["high_count"],

            "medium_count":
                risk["medium_count"],

            "low_count":
                risk["low_count"],

            "average_confidence":
                evidence["average_confidence"],

            "average_fraud_score":
                evidence["average_fraud_score"],

        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.4 - TOP RISK ENTITIES

    async def get_top_risk_entities(
        self,
        db,
        limit: int = 10,
    ):

        snapshot = await self._collect_all_snapshots(db)

        entities = snapshot.get_top_risk(limit)

        data = {

            "top_risk_entities":
                entities,

            "metadata": {

                "total_ranked":
                    snapshot.entity_count,

                "limit":
                    limit,

                "ranking":
                    "fraud_score",

                "sorted":
                    "descending",

            }

        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.5 - RISK DISTRIBUTION

    async def get_risk_distribution(self, db):
        """
        Semua data berasal dari DashboardSnapshot.

        Tidak menggunakan koleksi manual.
        Tidak menggunakan agregasi manual.
        """

        snapshot = await self._collect_all_snapshots(db)

        data = {
            "distribution": snapshot.analytics["risk"]["distribution"],
            "landscape": snapshot.analytics["risk"]["landscape"],
            "critical": snapshot.analytics["risk"]["critical_count"],
            "high": snapshot.analytics["risk"]["high_count"],
            "medium": snapshot.analytics["risk"]["medium_count"],
            "low": snapshot.analytics["risk"]["low_count"],
            "total_entities": snapshot.entity_count,
        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.6 - INTELLIGENCE TYPE DISTRIBUTION

    async def get_intelligence_type_distribution(self, db):
        """
        Sprint 2.2B

        Snapshot Reader Only.
        """

        snapshot = await self._collect_all_snapshots(db)
        
        data = {
            "distribution": snapshot.analytics["intelligence"]["distribution"],
            "average_fraud_score": snapshot.analytics["intelligence"]["average_fraud_score"],
            "total_entities": snapshot.analytics["intelligence"]["total_entities"],
        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.7 - EVIDENCE HEALTH

    async def get_evidence_health(self, db):

        snapshot = await self._collect_all_snapshots(db)

        avg = snapshot.analytics["evidence"]["average_confidence"]

        if avg >= 0.85:
            grade = "EXCELLENT"
        elif avg >= 0.70:
            grade = "GOOD"
        elif avg >= 0.50:
            grade = "NEEDS_REVIEW"
        else:
            grade = "POOR"

        data = {
            "average_confidence": avg,
            "average_fraud_score": snapshot.analytics["intelligence"]["average_fraud_score"],
            "distribution": snapshot.analytics["evidence"]["distribution"],
            "grade": grade,
        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.8 - ENTITY HISTORY / TIMELINE

    async def get_entity_history(
        self,
        entity_name: str,
        db,
    ):

        snapshot = await self._collect_all_snapshots(db)

        entity = snapshot.get_entity_by_name(entity_name)

        if entity is None:

            return dashboard_response_factory.build_response(
                snapshot,
                {
                    "entity": entity_name,
                    "found": False,
                },
            )

        relationship = entity.get(
            "relationship_metrics",
            {},
        )

        timeline = []

        if relationship.get("identity", 0):
            timeline.append(
                {
                    "type": "IDENTITY_MATCH",
                    "count": relationship["identity"],
                    "severity": "HIGH",
                }
            )

        if relationship.get("collusion", 0):
            timeline.append(
                {
                    "type": "PACKAGE_COLLUSION",
                    "count": relationship["collusion"],
                    "severity": "HIGH",
                }
            )

        if relationship.get("behavior", 0):
            timeline.append(
                {
                    "type": "PROCUREMENT_BEHAVIOR",
                    "count": relationship["behavior"],
                    "severity": "MEDIUM",
                }
            )

        if relationship.get("financial", 0):
            timeline.append(
                {
                    "type": "FINANCIAL_CLUSTER",
                    "count": relationship["financial"],
                    "severity": "MEDIUM",
                }
            )

        data = {
            "entity": entity["name"],
            "fraud_score": entity["fraud_score"],
            "risk_level": entity["risk_level"],
            "confidence": entity["confidence"],
            "timeline": timeline,
        }

        return dashboard_response_factory.build_response(
            snapshot,
            data,
        )

    # 9.9 - NETWORK SUMMARY

    async def get_network_summary(self, entity_name: str, db):
        start_time = time.time()

        snapshot = await self._collect_all_snapshots(db)

        entity = dashboard.get_entity_by_name(entity_name)

        if entity is None:
            return dashboard_response_factory.build_response(
                dashboard,
                {
                    "entity": entity_name,
                    "found": False,
                },
            )

        metrics = entity["relationship_metrics"]

        node_count = (
            metrics.get("identity", 0)
            + metrics.get("collusion", 0)
            + metrics.get("behavior", 0)
            + metrics.get("financial", 0)
            + 1
        )

        relation_count = max(node_count - 1, 0)

        data = {
            "entity": entity_name,
            "statistics": {
                "nodes": node_count,
                "relations": relation_count,
                "patterns": len(entity["patterns"])
            },
            "risk": {
                "score": entity["fraud_score"],
                "level": entity["risk_level"],
                "confidence": entity["confidence"],
            },
            "relationship_metrics": metrics
        }

        return dashboard_response_factory.build_response(snapshot, data)

    # 9.10 - ENTITY EXPLAIN

    async def explain_entity(self, entity_name: str, db):
        start_time = time.time()

        snapshot = await self._collect_all_snapshots(db)

        entity = dashboard.get_entity_by_name(entity_name)

        data = {
            "entity": entity_name,
            "fraud_score": entity["fraud_score"],
            "risk_level": snapshot["risk_level"],
            "confidence": snapshot["confidence"],
            "risk_explanation": snapshot["risk_explanation"],
            "score_breakdown": snapshot["score_breakdown"],
            "patterns": entity["patterns"],
            "relationship_metrics": snapshot["relationship_metrics"],
            "evidence": entity["evidence"][:5]  # Limit evidence untuk response
        }

        return dashboard_response_factory.build_response(snapshot, data)

    # 9.11 - ENTITY NETWORK

    async def get_entity_network(self, entity_name: str, db):
        start_time = time.time()

        graph = await entity_graph_intelligence_service.get_entity_network(
            entity_name,
            db
        )

        return dashboard_response_factory.build_response(snapshot, data)

    # 9.12 - DASHBOARD STATUS

    async def get_dashboard_status(self, db):

        snapshot = await self._collect_all_snapshots(db)

        data = {

            "snapshot_id": snapshot.snapshot_id,

            "snapshot_version": snapshot.snapshot_version,

            "generated_at": snapshot.generated_at.isoformat(),

            "entity_count": snapshot.entity_count,

            "collector_metrics": snapshot.collector_metrics,

            "execution_ms": snapshot.execution_ms,

            "cache_hit": snapshot.cache_hit,

            "analytics_available": list(snapshot.analytics.keys()),

            "ranking_available": list(snapshot.rankings.keys()),

        }

        return dashboard_response_factory.build_health_response(
            snapshot,
            data,
        )

    # 9.13 - REFRESH CACHE

    async def refresh_cache(self, db):

        self.clear_cache()
        self.statistics_cache = None
        self.statistics_timestamp = None

        snapshot = await self._collect_all_snapshots(
            db,
            refresh=True,
        )

        return dashboard_response_factory.build_response(
            snapshot,
            {
                "status": "SUCCESS",
                "snapshot_id": snapshot.snapshot_id,
                "entity_count": snapshot.entity_count,
                "execution_ms": snapshot.execution_ms,
                "collector_metrics": snapshot.collector_metrics,
            },
        )


# ============================================================
# SINGLETON
# ============================================================

dashboard_intelligence_analytics_service = DashboardIntelligenceAnalyticsService()