# backend/graph/transformers/rup_record_to_graph_node.py

"""Deterministic transformer: RUP record → GraphNode."""

from backend.graph.domain.node import GraphNode
from backend.graph.dto.rup_record_dto import RupRecordDTO


class RupRecordToGraphNode:
    """Deterministic transformer: RUP record → GraphNode.

    Invariants:
        - business_key = "RUP:" + str(record.id)
        - source_id = record.id
        - entity_type = "procurement_record"
        - name = record.name
        - extra_data["source"] = all source metadata
    """

    @staticmethod
    def transform(record: RupRecordDTO) -> GraphNode:
        """Transform a single RUP record to a GraphNode."""
        return GraphNode(
            business_key=f"RUP:{record.id}",
            entity_type="procurement_record",
            name=record.name,
            source_id=record.id,
            extra_data={
                "source": {
                    "package_code": record.package_code,
                    "rup_code": record.rup_code,
                    "vendor": record.vendor,
                    "year": record.year,
                    "total_value": (
                        str(record.total_value)
                        if record.total_value is not None
                        else None
                    ),
                    "pdn_value": (
                        str(record.pdn_value)
                        if record.pdn_value is not None
                        else None
                    ),
                    "institution": record.institution,
                    "work_unit": record.work_unit,
                    "fund_source": record.fund_source,
                    "procurement_method": record.procurement_method,
                    "procurement_type": record.procurement_type,
                    "status": record.status,
                    "transaction_source": record.transaction_source,
                }
            }
        )
