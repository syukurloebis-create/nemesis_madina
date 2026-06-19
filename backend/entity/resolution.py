# entity/resolution.py - Entity Resolution Service
import re
import logging
from typing import List, Dict, Optional, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class EntityResolutionService:
    """Service untuk entity resolution dan normalisasi"""

    @staticmethod
    def normalize_entity_name(name: str) -> str:
        """
        Normalize entity name untuk standarisasi

        Contoh:
        - "PT. ABC" → "PT ABC"
        - "PT ABC" → "PT ABC"
        - "CV. ABC" → "CV ABC"
        - "PT ABC (Persero)" → "PT ABC"
        """
        if not name:
            return ""

        # Clean extra spaces
        name = re.sub(r'\s+', ' ', name.strip())

        # Remove special characters except dot and dash
        name = re.sub(r'[^\w\s\.\-]', '', name)

        # Standardize PT
        name = re.sub(r'^PT\.?\s*', 'PT ', name, flags=re.IGNORECASE)

        # Standardize CV
        name = re.sub(r'^CV\.?\s*', 'CV ', name, flags=re.IGNORECASE)

        # Remove (Persero) etc
        name = re.sub(r'\s*\([^)]*\)', '', name)

        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()

        return name.upper()

    @staticmethod
    def resolve_entities(
        entities: List[Dict[str, Any]],
        threshold: float = 0.85
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Resolve duplicate entities berdasarkan similarity

        Args:
            entities: List of entity dicts with 'name' field
            threshold: Similarity threshold (0-1)

        Returns:
            Dictionary with resolved entity names as keys
        """
        resolved = {}
        seen = set()

        for entity in entities:
            name = EntityResolutionService.normalize_entity_name(
                entity.get("name", "")
            )
            if not name:
                continue

            matched = False
            for resolved_name in seen:
                similarity = SequenceMatcher(
                    None,
                    name,
                    resolved_name
                ).ratio()

                if similarity >= threshold:
                    if resolved_name not in resolved:
                        resolved[resolved_name] = []
                    resolved[resolved_name].append(entity)
                    matched = True
                    break

            if not matched:
                seen.add(name)
                resolved[name] = [entity]

        return resolved

    @staticmethod
    def find_duplicates(
        entities: List[Dict[str, Any]],
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Find duplicate entities

        Returns list of duplicate groups
        """
        resolved = EntityResolutionService.resolve_entities(entities, threshold)
        duplicates = []

        for name, group in resolved.items():
            if len(group) > 1:
                duplicates.append({
                    "canonical_name": name,
                    "count": len(group),
                    "entities": group
                })

        return duplicates

    @staticmethod
    def get_canonical_name(
        name: str,
        entities: List[Dict[str, Any]],
        threshold: float = 0.85
    ) -> Optional[str]:
        """Get canonical name for an entity"""
        normalized = EntityResolutionService.normalize_entity_name(name)

        for entity in entities:
            entity_name = EntityResolutionService.normalize_entity_name(
                entity.get("name", "")
            )
            if SequenceMatcher(None, normalized, entity_name).ratio() >= threshold:
                return entity_name

        return None
