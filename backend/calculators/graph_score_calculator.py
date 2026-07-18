"""
Graph Score Calculator — Pure Function.
"""

from dataclasses import dataclass

from backend.dtos.collector_dtos import GraphCollectorDTO
from backend.calculators.config import GraphWeights
from backend.domain.enums import EngineStatus


@dataclass(frozen=True, slots=True)
class CalculatedGraph:
    """Hasil perhitungan dari GraphScoreCalculator."""
    score: float
    density: float
    entity_score: float
    relationship_score: float
    engine_status: EngineStatus = EngineStatus.OK


class GraphScoreCalculator:
    """Graph Score Calculator — Pure Function."""

    @classmethod
    def calculate(
        cls,
        dto: GraphCollectorDTO,
        weights: GraphWeights
    ) -> CalculatedGraph:
        """Calculate graph score from DTO."""
        if dto.entities == 0:
            return CalculatedGraph(
                score=0,
                density=0,
                entity_score=0,
                relationship_score=0,
                engine_status=EngineStatus.OK,
            )

        # Density = relationships / entities
        density = dto.relationships / dto.entities if dto.entities > 0 else 0
        
        # ✅ Entity score: menggunakan parameter dari weights
        entity_score = min(weights.max_entity_score, dto.entities * weights.entity_scale)
        
        # ✅ Relationship score: menggunakan parameter dari weights
        relationship_score = min(weights.max_relationship_score, density * weights.density_scale)
        
        # Weighted score
        score = (
            entity_score * weights.entity_weight +
            relationship_score * weights.relationship_weight
        )

        return CalculatedGraph(
            score=round(score, 2),
            density=round(density, 4),
            entity_score=round(entity_score, 2),
            relationship_score=round(relationship_score, 2),
            engine_status=dto.engine_status,
        )