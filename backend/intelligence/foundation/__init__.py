"""
Intelligence Data Foundation
Entity Resolution, Evidence Registry, Feature Store, Data Quality, Knowledge Graph
"""
from .entity_resolution import EntityResolutionEngine, ResolvedEntity, entity_resolver
from .evidence_registry import EvidenceRegistry, EvidenceRecord, evidence_registry
from .feature_store import FeatureStore, FeatureDefinition, FeatureType, FeatureSource, feature_store
from .data_quality import DataQualityPipeline, QualityIssue, Severity, data_quality
from .knowledge_graph import KnowledgeGraph, KnowledgeNode, KnowledgeEdge, knowledge_graph

__all__ = [
    'EntityResolutionEngine', 'ResolvedEntity', 'entity_resolver',
    'EvidenceRegistry', 'EvidenceRecord', 'evidence_registry',
    'FeatureStore', 'FeatureDefinition', 'FeatureType', 'FeatureSource', 'feature_store',
    'DataQualityPipeline', 'QualityIssue', 'Severity', 'data_quality',
    'KnowledgeGraph', 'KnowledgeNode', 'KnowledgeEdge', 'knowledge_graph'
]
