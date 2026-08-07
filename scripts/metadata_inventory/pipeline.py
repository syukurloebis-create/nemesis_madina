# scripts/metadata_inventory/pipeline.py

from dataclasses import dataclass
from typing import Any, Dict, List
from .dtos import AuditResult
from .collectors import Collector
from .normalizers import Normalizer
from .analyzers import Analyzer
from .classifiers import Classifier
from .scoring import ScoringEngine
from .recommendations import RecommendationEngine
from .reporters import ReporterManager

class AuditPipeline:
    """Pipeline dengan PipelineContext sebagai kontrak."""
    
    def __init__(self, context: PipelineContext):
        self.context = context
        self._validate_contracts()
    
    def _validate_contracts(self):
        """Validasi semua contract versions di startup."""
        if self.context.contract_version != CONTRACT_VERSION:
            raise ContractVersionError(
                f"Pipeline context contract v{self.context.contract_version} "
                f"does not match framework contract v{CONTRACT_VERSION}"
            )

    def run(self) -> AuditResult:
        # Pipeline stages dengan context yang terdefinisi
        discovery = self.discover(self.context)
        raw = self.collect(discovery, self.context)
        normalized = self.normalize(raw, self.context)
        findings = self.analyze(normalized, self.context)
        recommendations = self.recommend(findings, self.context)
        score = self.score(findings, self.context)
        
        result = (AuditResultBuilder()
                  .with_metadata(normalized.metadata)
                  .with_relationships(normalized.relationships)
                  .with_foreign_keys(normalized.foreign_keys)
                  .with_findings(findings)
                  .with_recommendations(recommendations)
                  .with_health_score(score)
                  .build())
        
        return result