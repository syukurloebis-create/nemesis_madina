"""
Entity Resolution Tests
"""
import pytest
from intelligence.foundation.entity_resolution import EntityResolutionEngine

class TestEntityResolution:
    """Test entity resolution engine"""

    def setup_method(self):
        self.engine = EntityResolutionEngine()

    def test_normalize_name(self):
        """Test name normalization"""
        assert self.engine.normalize_name("PT ABC Jaya") == "abc jaya"
        assert self.engine.normalize_name("CV Makmur Sejahtera") == "makmur sejahtera"
        assert self.engine.normalize_name("Toko Sembako 99") == "sembako 99"

    def test_get_name_similarity(self):
        """Test name similarity calculation"""
        sim = self.engine.get_name_similarity("PT ABC", "ABC")
        assert sim > 0.8

        sim = self.engine.get_name_similarity("CV Makmur", "Makmur Sejahtera")
        assert sim > 0.6

    def test_resolve_single_entity(self):
        """Test resolving a single entity"""
        source = {
            "name": "PT ABC Jaya",
            "entity_type": "COMPANY",
            "address": "Jl. Sudirman No. 1"
        }
        entity = self.engine.resolve(source)
        assert entity.canonical_name == "PT ABC Jaya"
        assert entity.entity_type == "COMPANY"
        assert entity.confidence >= 0.7

    def test_resolve_duplicate_entity(self):
        """Test resolving duplicate entity"""
        source1 = {"name": "PT ABC Jaya"}
        source2 = {"name": "ABC Jaya", "phone": "08123456789"}

        entity1 = self.engine.resolve(source1)
        entity2 = self.engine.resolve(source2)

        # Should be the same entity
        assert entity1.id == entity2.id
        assert "ABC Jaya" in entity1.aliases
        assert entity1.attributes.get("phone") == "08123456789"

    def test_merge_entities(self):
        """Test merging two entities"""
        source1 = {"name": "PT ABC"}
        source2 = {"name": "ABC Corp"}

        entity1 = self.engine.resolve(source1)
        entity2 = self.engine.resolve(source2)

        # Should be different initially
        assert entity1.id != entity2.id

        # Merge
        merged = self.engine.merge_entities(entity1.id, entity2.id)
        assert "PT ABC" in merged.aliases or "ABC Corp" in merged.aliases
        assert len(self.engine.resolved_entities) == 1

    def test_find_duplicates(self):
        """Test finding duplicates"""
        sources = [
            {"name": "PT ABC Jaya"},
            {"name": "ABC Jaya"},
            {"name": "CV XYZ"},
            {"name": "XYZ"}
        ]

        for source in sources:
            self.engine.resolve(source)

        duplicates = self.engine.find_duplicates()
        assert len(duplicates) > 0

    def test_auto_merge_duplicates(self):
        """Test auto-merge duplicates"""
        sources = [
            {"name": "PT ABC Jaya"},
            {"name": "ABC Jaya"},
            {"name": "CV XYZ"},
            {"name": "XYZ"}
        ]

        for source in sources:
            self.engine.resolve(source)

        initial_count = len(self.engine.resolved_entities)
        merged = self.engine.auto_merge_duplicates()
        final_count = len(self.engine.resolved_entities)

        assert merged > 0
        assert final_count < initial_count