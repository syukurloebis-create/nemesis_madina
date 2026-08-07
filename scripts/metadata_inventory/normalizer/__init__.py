# scripts/metadata_inventory/normalizers/__init__.py
from .base import Normalizer
from .metadata_normalizer import MetadataNormalizer
from .relationship_normalizer import RelationshipNormalizer
from .fk_normalizer import FKNormalizer

class NormalizerRegistry:
    """Centralized normalizer registry."""
    
    def __init__(self):
        self.normalizers = [
            MetadataNormalizer(),
            RelationshipNormalizer(),
            FKNormalizer(),
        ]
    
    def normalize(self, raw_collection: 'RawCollection') -> 'AuditResult':
        """Normalize semua raw data menjadi DTO."""
        normalized = {}
        
        for normalizer in self.normalizers:
            result = normalizer.normalize(raw_collection)
            normalized[normalizer.name] = result
        
        # Build AuditResult dari semua hasil normalisasi
        return self.build_result(normalized)