"""Vendor Node Factory — Creates vendor nodes from RUP data."""

from typing import List, Dict, Set, Optional
from backend.graph.domain.node import GraphNode


class VendorNodeFactory:
    """Factory for creating vendor nodes from RUP records."""

    @staticmethod
    def create_vendor_nodes(
        rows: List[Dict],
        vendor_field: str = "nama_penyedia",
    ) -> List[GraphNode]:
        """
        Create vendor nodes from RUP records.

        Args:
            rows: List of RUP record dicts
            vendor_field: Field name for vendor name

        Returns:
            List of GraphNode with entity_type = "vendor"
        """
        vendor_map: Dict[str, Dict] = {}

        for row in rows:
            vendor_raw = row.get(vendor_field)
            if vendor_raw is None:
                continue
            vendor_name = str(vendor_raw).strip()
            if not vendor_name:
                continue

            # Normalize vendor name for deduplication
            vendor_key = vendor_name.lower().strip()

            if vendor_key not in vendor_map:
                vendor_map[vendor_key] = {
                    "name": vendor_name,
                    "package_codes": set(),
                    "years": set(),
                    "row_count": 0,
                    "total_value": 0,
                }

            vendor_map[vendor_key]["row_count"] += 1

            package_code = row.get("kode_paket")
            if package_code:
                vendor_map[vendor_key]["package_codes"].add(str(package_code))

            year = row.get("tahun_anggaran")
            if year is not None:
                vendor_map[vendor_key]["years"].add(year)

            total_value = row.get("total_nilai")
            if total_value is not None:
                vendor_map[vendor_key]["total_value"] += float(total_value)

        nodes = []
        for vendor_key, data in vendor_map.items():
            node = GraphNode(
                business_key=vendor_key,
                entity_type="vendor",
                name=data["name"],
                source_id=None,
                extra_data={
                    "source": {
                        "row_count": data["row_count"],
                        "package_count": len(data["package_codes"]),
                        "years": sorted(data["years"]),
                        "total_value": data["total_value"],
                    }
                },
            )
            nodes.append(node)

        return nodes
