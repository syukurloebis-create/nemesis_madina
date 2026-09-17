"""Collusion Detector — Detect vendor collusion from RUP data."""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge


class CollusionDetector:
    """Detect collusion patterns between vendors."""

    @staticmethod
    def detect(
        rows: List[Dict],
        vendor_field: str = "nama_penyedia",
        package_field: str = "kode_paket",
        min_shared_packages: int = 2,
    ) -> List[GraphEdge]:
        """
        Detect vendor collusion from RUP records.

        Args:
            rows: List of RUP record dicts
            vendor_field: Field name for vendor name
            package_field: Field name for package code
            min_shared_packages: Minimum shared packages to qualify

        Returns:
            List of GraphEdge with relationship_type = "COLLUSION"
        """
        # 1. Build vendor → packages mapping
        vendor_packages: Dict[str, Set[str]] = defaultdict(set)
        for row in rows:
            vendor = row.get(vendor_field, "").strip().lower()
            package = row.get(package_field, "").strip()
            if vendor and package:
                vendor_packages[vendor].add(package)

        # 2. Calculate package count per vendor
        vendor_package_count = {
            vendor: len(packages)
            for vendor, packages in vendor_packages.items()
        }

        # 3. Detect collusion pairs
        vendors = list(vendor_packages.keys())
        edges = []

        for i, v1 in enumerate(vendors):
            packages_1 = vendor_packages[v1]
            for v2 in vendors[i + 1:]:
                packages_2 = vendor_packages[v2]
                shared = packages_1 & packages_2

                if len(shared) >= min_shared_packages:
                    weight = len(shared) / max(
                        vendor_package_count[v1],
                        vendor_package_count[v2],
                    )

                    edge = GraphEdge(
                        source_key=v1,
                        target_key=v2,
                        relationship_type="COLLUSION",
                        weight=weight,
                        extra_data={
                            "shared_packages": len(shared),
                            "sample_packages": list(shared)[:5],
                            "package_count_a": vendor_package_count[v1],
                            "package_count_b": vendor_package_count[v2],
                        },
                    )
                    edges.append(edge)

        return edges
