# ============================================================
# dashboard_snapshot_builder.py
# Sprint 2.2A - Snapshot Builder
#
# Pure builder.
#
# Tidak mengetahui:
#   - SQLAlchemy
#   - Database
#   - FastAPI
#   - Graph Engine
#
# Hanya menerima List[Dict] entity intelligence
# kemudian menghasilkan DashboardSnapshot.
# ============================================================

from __future__ import annotations

import time

from collections import Counter

from typing import Any
from typing import Dict
from typing import List

from backend.services.dashboard_snapshot import SnapshotFactory


class DashboardSnapshotBuilder:
    """
    Pure Snapshot Builder.

    Input:
        List entity intelligence

    Output:
        DashboardSnapshot immutable
    """

    # ========================================================
    # BUILD ANALYTICS
    # ========================================================

    @classmethod
    def build_analytics(
        cls,
        entities: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        risk_distribution = Counter()

        evidence_distribution = Counter()

        intelligence_distribution = Counter()

        pattern_distribution = Counter()

        fraud_sum = 0.0

        confidence_sum = 0.0

        relationship_totals = {
            "identity": 0,
            "collusion": 0,
            "behavior": 0,
            "financial": 0,
        }

        total_patterns = 0

        for entity in entities:

            risk_distribution[
                entity.get(
                    "risk_level",
                    "LOW",
                )
            ] += 1

            evidence_distribution[
                entity.get(
                    "evidence_grade",
                    "UNKNOWN",
                )
            ] += 1

            intelligence_distribution[
                entity.get(
                    "intelligence_type",
                    "UNKNOWN",
                )
            ] += 1

            fraud_sum += entity.get(
                "fraud_score",
                0,
            )

            confidence_sum += entity.get(
                "confidence",
                0,
            )

            #
            # Pattern Analytics
            #

            patterns = entity.get(
                "patterns",
                [],
            )

            total_patterns += len(patterns)

            for pattern in patterns:

                pattern_distribution[
                    pattern.get(
                        "type",
                        "UNKNOWN",
                    )
                ] += 1

            #
            # Relationship Metrics
            #

            relationship = entity.get(
                "relationship_metrics",
                {},
            )

            relationship_totals["identity"] += relationship.get(
                "identity",
                0,
            )

            relationship_totals["collusion"] += relationship.get(
                "collusion",
                0,
            )

            relationship_totals["behavior"] += relationship.get(
                "behavior",
                0,
            )

            relationship_totals["financial"] += relationship.get(
                "financial",
                0,
            )

        total = len(entities)

        average_fraud = (
            round(fraud_sum / total, 2)
            if total
            else 0
        )

        average_confidence = (
            round(confidence_sum / total, 2)
            if total
            else 0
        )

        graph_edge_count = (
            relationship_totals["identity"]
            + relationship_totals["collusion"]
            + relationship_totals["behavior"]
            + relationship_totals["financial"]
        )

        graph_density = 0.0

        if total > 1:

            graph_density = round(
                graph_edge_count
                /
                (total * (total - 1)),
                5,
            )

        return {

            #
            # Risk
            #

            "risk_distribution":
                dict(risk_distribution),

            "critical_count":
                risk_distribution.get(
                    "CRITICAL",
                    0,
                ),

            "high_count":
                risk_distribution.get(
                    "HIGH",
                    0,
                ),

            "medium_count":
                risk_distribution.get(
                    "MEDIUM",
                    0,
                ),

            "low_count":
                risk_distribution.get(
                    "LOW",
                    0,
                ),

            #
            # Evidence
            #

            "evidence_distribution":
                dict(evidence_distribution),

            #
            # Intelligence
            #

            "intelligence_distribution":
                dict(intelligence_distribution),

            #
            # Scores
            #

            "average_fraud_score":
                average_fraud,

            "average_confidence":
                average_confidence,

            #
            # Patterns
            #

            "pattern_distribution":
                dict(pattern_distribution),

            "top_patterns":
                pattern_distribution.most_common(10),

            "total_patterns":
                total_patterns,

            #
            # Network
            #

            "relationship_totals":
                relationship_totals,

            "graph_metrics": {

                "node_count":
                    total,

                "edge_count":
                    graph_edge_count,

                "average_degree":
                    round(
                        graph_edge_count / total,
                        2,
                    )
                    if total
                    else 0,

                "density":
                    graph_density,

            },

            #
            # Misc
            #

            "entity_count":
                total,

        }

    # ========================================================
    # BUILD RANKINGS
    # ========================================================

    @classmethod
    def build_rankings(
        cls,
        entities: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:

        fraud_rank = sorted(
            entities,
            key=lambda x:
                x.get(
                    "fraud_score",
                    0,
                ),
            reverse=True,
        )

        confidence_rank = sorted(
            entities,
            key=lambda x:
                x.get(
                    "confidence",
                    0,
                ),
            reverse=True,
        )

        network_rank = sorted(
            entities,
            key=lambda x:
                len(
                    x.get(
                        "patterns",
                        [],
                    )
                ),
            reverse=True,
        )

        return {

            "fraud":
                fraud_rank,

            "confidence":
                confidence_rank,

            "network":
                network_rank,

        }


    # ============================================================
    # Collector Metrics Builder
    # ============================================================

    @classmethod
    def create_collector_metrics(
        cls,
        load_entities_ms: float = 0.0,
        graph_ms: float = 0.0,
        analytics_ms: float = 0.0,
        ranking_ms: float = 0.0,
        total_ms: float = 0.0,
    ) -> Dict[str, float]:
        """
        Build collector performance metrics.

        Digunakan oleh collector untuk mencatat waktu setiap fase
        tanpa membuat collector mengetahui struktur metrics snapshot.

        Parameters
        ----------
        load_entities_ms
            Waktu query graph_entities.

        graph_ms
            Waktu enrichment Graph Intelligence.

        analytics_ms
            Waktu build analytics.

        ranking_ms
            Waktu build rankings.

        total_ms
            Total waktu collector.
        """

        return {

            "load_entities_ms":
                round(load_entities_ms, 2),

            "graph_intelligence_ms":
                round(graph_ms, 2),

            "analytics_ms":
                round(analytics_ms, 2),

            "ranking_ms":
                round(ranking_ms, 2),

            "total_ms":
                round(total_ms, 2),

            "entity_processing_ms":
                round(
                    graph_ms + analytics_ms + ranking_ms,
                    2,
                ),

            "collector_version":
                "2.2",

        }

    # ========================================================
    # BUILD SNAPSHOT
    # ========================================================

    @classmethod
    def build(
        cls,
        entities: List[Dict],
        collector_metrics: Optional[Dict[str, float]] = None,
        execution_ms: float = 0.0,
        cache_hit: bool = False,
    ):

        if collector_metrics is None:
            collector_metrics = cls.create_collector_metrics(
                total_ms=execution_ms
            )

        analytics = cls.build_analytics(
            entities,
        )

        rankings = cls.build_rankings(
            entities,
        )

        return SnapshotFactory.create_from_data(

            entities=entities,

            analytics=analytics,

            rankings=rankings,

            collector_metrics=collector_metrics,

            execution_ms=execution_ms,

            cache_hit=cache_hit,

        )

    # ========================================================
    # BUILD EMPTY SNAPSHOT
    # ========================================================

    @classmethod
    def build_empty(cls):

        return SnapshotFactory.create_empty()

    # ========================================================
    # PERFORMANCE TIMER
    # ========================================================

    @staticmethod
    def create_collector_metrics(
        *,
        load_entities_ms: float = 0.0,
        graph_ms: float = 0.0,
        analytics_ms: float = 0.0,
        ranking_ms: float = 0.0,
        total_ms: float = 0.0,
    ) -> Dict[str, float]:

        return {

            "load_entities_ms":
                round(load_entities_ms, 2),

            "graph_intelligence_ms":
                round(graph_ms, 2),

            "analytics_ms":
                round(analytics_ms, 2),

            "ranking_ms":
                round(ranking_ms, 2),

            "total_ms":
                round(total_ms, 2),

        }


# ============================================================
# Singleton
# ============================================================

dashboard_snapshot_builder = DashboardSnapshotBuilder()