"""RUP to Graph Transformer — Full transformation with nodes and edges."""

from typing import List, Dict, Tuple
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.transformers.rup_record_to_graph_node import RupRecordToGraphNode
from backend.graph.transformers.vendor_node_factory import VendorNodeFactory
from backend.graph.transformers.collusion_detector import CollusionDetector


class RupToGraphTransformer:
    """Full transformer: RUP rows → GraphNodes + GraphEdges."""

    @staticmethod
    def transform(rows: List[Dict]) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # 1. Procurement Record nodes (RUP rows)
        for row in rows:
            from backend.graph.dto.rup_record_dto import RupRecordDTO
            from decimal import Decimal

            record = RupRecordDTO(
                id=row.get("id"),
                package_code=row.get("kode_paket", ""),
                name=row.get("nama_paket", ""),
                vendor=row.get("nama_penyedia", ""),
                year=row.get("tahun_anggaran"),
                total_value=Decimal(str(row.get("total_nilai", 0))) if row.get("total_nilai") else None,
                pdn_value=Decimal(str(row.get("nilai_pdn", 0))) if row.get("nilai_pdn") else None,
                institution=row.get("nama_instansi"),
                work_unit=row.get("satuan_kerja"),
                fund_source=row.get("sumber_dana"),
                procurement_method=row.get("metode_pengadaan"),
                procurement_type=row.get("jenis_pengadaan"),
                status=row.get("status_paket"),
                transaction_source=row.get("sumber_transaksi"),
            )
            node = RupRecordToGraphNode.transform(record)
            nodes.append(node)

        # 2. Vendor nodes
        vendor_nodes = VendorNodeFactory.create_vendor_nodes(rows)
        nodes.extend(vendor_nodes)

        # 3. Vendor-Has-Package edges (UNIQUE vendor-package pairs)
        pair_to_rup_ids: Dict[Tuple[str, str], List[int]] = {}
        for row in rows:
            vendor = row.get("nama_penyedia", "").strip().lower()
            package_code = row.get("kode_paket", "").strip()
            rup_id = row.get("id")
            if vendor and package_code and rup_id:
                key = (vendor, package_code)
                if key not in pair_to_rup_ids:
                    pair_to_rup_ids[key] = []
                pair_to_rup_ids[key].append(rup_id)

        # Create one edge per unique vendor-package pair
        for (vendor, package_code), rup_ids in pair_to_rup_ids.items():
            target_rup_id = min(rup_ids)
            edge = GraphEdge(
                source_key=vendor,
                target_key=f"RUP:{target_rup_id}",
                relationship_type="VENDOR_HAS_PACKAGE",
                weight=1.0,
                extra_data={
                    "package_code": package_code,
                    "rup_ids": rup_ids,
                    "row_count": len(rup_ids),
                },
            )
            edges.append(edge)

        # 4. Collusion edges
        collusion_edges = CollusionDetector.detect(rows)
        edges.extend(collusion_edges)

        return nodes, edges
