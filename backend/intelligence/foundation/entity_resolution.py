"""
Entity Resolution Engine
Mendeteksi dan menggabungkan entity yang sama dari berbagai sumber
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
import re
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class ResolvedEntity:
    """Entity yang telah di-resolve"""
    id: UUID = field(default_factory=uuid4)
    canonical_name: str = ""
    aliases: List[str] = field(default_factory=list)
    entity_type: str = "unknown"
    confidence: float = 0.0
    source_records: List[Dict[str, Any]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_alias(self, alias: str) -> None:
        """Tambahkan alias jika belum ada"""
        if alias and alias not in self.aliases:
            self.aliases.append(alias)
            self.updated_at = datetime.now()

    def add_source(self, source: Dict[str, Any]) -> None:
        """Tambahkan source record"""
        self.source_records.append(source)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Konversi ke dictionary"""
        return {
            "id": str(self.id),
            "canonical_name": self.canonical_name,
            "aliases": self.aliases,
            "entity_type": self.entity_type,
            "confidence": self.confidence,
            "source_records": self.source_records,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class EntityResolutionEngine:
    """Engine untuk entity resolution"""

    def __init__(self):
        self.entities: Dict[str, ResolvedEntity] = {}
        self.similarity_threshold = 0.8
        self.min_name_length = 3

    def normalize_name(self, name: str) -> str:
        """Normalisasi nama untuk perbandingan"""
        if not name:
            return ""
        # Hapus PT, CV, Tbk, dll
        name = re.sub(r'\b(PT|CV|UD|Tbk|TBK|Ltd|LLC|Inc|Corp|Corporation)\b', '', name, flags=re.IGNORECASE)
        # Hapus karakter spesial
        name = re.sub(r'[^\w\s]', '', name)
        # Hapus extra whitespace
        name = ' '.join(name.split())
        return name.strip().lower()

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Hitung similarity antara dua nama"""
        if not name1 or not name2:
            return 0.0
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        if not norm1 or not norm2:
            return 0.0
        return SequenceMatcher(None, norm1, norm2).ratio()

    def resolve_entity(
        self,
        name: str,
        entity_type: str = "unknown",
        source: Optional[Dict[str, Any]] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> ResolvedEntity:
        """
        Resolve entity: cari existing atau buat baru
        """
        # Cari entity yang sudah ada
        best_match = None
        best_score = 0.0

        for entity_id, entity in self.entities.items():
            # Check canonical name
            score = self.calculate_similarity(name, entity.canonical_name)
            if score > best_score:
                best_score = score
                best_match = entity

            # Check aliases
            for alias in entity.aliases:
                score = self.calculate_similarity(name, alias)
                if score > best_score:
                    best_score = score
                    best_match = entity

        # Jika similarity cukup tinggi, gunakan existing entity
        if best_match and best_score >= self.similarity_threshold:
            best_match.add_alias(name)
            if source:
                best_match.add_source(source)
            if attributes:
                best_match.attributes.update(attributes)
            logger.info(f"Entity resolved to: {best_match.canonical_name} (score: {best_score:.2f})")
            return best_match

        # Buat entity baru
        entity = ResolvedEntity(
            canonical_name=name,
            entity_type=entity_type,
            confidence=best_score,
            attributes=attributes or {}
        )
        if source:
            entity.add_source(source)
        self.entities[str(entity.id)] = entity
        logger.info(f"New entity created: {name} (ID: {entity.id})")
        return entity

    def get_entity(self, entity_id: str) -> Optional[ResolvedEntity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def find_entity_by_name(self, name: str) -> Optional[ResolvedEntity]:
        """Find entity by name"""
        for entity in self.entities.values():
            if entity.canonical_name == name or name in entity.aliases:
                return entity
        return None

    def merge_entities(self, entity_id_1: str, entity_id_2: str) -> Optional[ResolvedEntity]:
        """Merge dua entity menjadi satu"""
        entity1 = self.get_entity(entity_id_1)
        entity2 = self.get_entity(entity_id_2)
        if not entity1 or not entity2:
            return None

        # Gunakan entity dengan lebih banyak source sebagai master
        if len(entity1.source_records) >= len(entity2.source_records):
            master, slave = entity1, entity2
        else:
            master, slave = entity2, entity1

        # Pindahkan semua alias dan source dari slave ke master
        for alias in slave.aliases:
            master.add_alias(alias)
        for source in slave.source_records:
            master.add_source(source)
        master.attributes.update(slave.attributes)

        # Update confidence
        master.confidence = max(master.confidence, slave.confidence)

        # Hapus slave
        del self.entities[str(slave.id)]

        logger.info(f"Merged {slave.canonical_name} into {master.canonical_name}")
        return master

    def get_all_entities(self) -> List[ResolvedEntity]:
        """Get semua entities"""
        return list(self.entities.values())

    def get_entities_by_type(self, entity_type: str) -> List[ResolvedEntity]:
        """Get entities by type"""
        return [e for e in self.entities.values() if e.entity_type == entity_type]

    def resolve_batch(
        self,
        entities: List[Dict[str, Any]]
    ) -> List[ResolvedEntity]:
        """Resolve multiple entities sekaligus"""
        results = []
        for entity_data in entities:
            resolved = self.resolve_entity(
                name=entity_data.get("name", ""),
                entity_type=entity_data.get("type", "unknown"),
                source=entity_data.get("source"),
                attributes=entity_data.get("attributes")
            )
            results.append(resolved)
        return results

    def export_entity_graph(self) -> Dict[str, Any]:
        """Export entity graph untuk visualisasi"""
        nodes = []
        edges = []

        for entity in self.entities.values():
            # Node untuk entity utama
            nodes.append({
                "id": str(entity.id),
                "label": entity.canonical_name,
                "type": entity.entity_type,
                "confidence": entity.confidence
            })
            # Edge untuk alias
            for alias in entity.aliases:
                alias_id = f"alias_{hash(alias)}"
                nodes.append({
                    "id": alias_id,
                    "label": alias,
                    "type": "alias",
                    "confidence": 0.5
                })
                edges.append({
                    "source": str(entity.id),
                    "target": alias_id,
                    "type": "alias_of"
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "total_entities": len(self.entities)
        }


# Singleton instance
entity_resolver = EntityResolutionEngine()