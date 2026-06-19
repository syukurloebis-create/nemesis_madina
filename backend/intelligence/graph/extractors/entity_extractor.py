"""
Entity Extraction from Events and Case Metadata
"""

from typing import List, Dict, Any, Set
import re


class EntityExtractor:
    """
    Extract entities from case data with strict type validation.
    """
    
    VALID_ENTITY_TYPES = {"person", "company", "account", "asset"}
    
    # Pattern untuk deteksi company (Indonesia)
    COMPANY_PATTERNS = [
        r'PT\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
        r'CV\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
        r'Persero\s+[A-Z][a-z]+',
        r'Yayasan\s+[A-Z][a-z]+',
    ]
    
    def extract_from_case_metadata(self, metadata: Dict) -> List[Dict]:
        """
        Extract entities from case_metadata (MOST IMPORTANT)
        This is where companies and suspects are defined.
        """
        entities = []
        
        # Extract companies from companies array
        companies = metadata.get("companies", [])
        for company in companies:
            if company and len(company) > 2:
                entities.append({
                    "type": "company",
                    "name": company,
                    "confidence": 0.95,
                    "source": "case_metadata_companies",
                })
        
        # Extract suspects/persons
        suspects = metadata.get("suspects", [])
        for suspect in suspects:
            if suspect and len(suspect) > 2:
                entities.append({
                    "type": "person",
                    "name": suspect,
                    "confidence": 0.9,
                    "source": "case_metadata_suspects",
                })
        
        # Extract from transactions
        transactions = metadata.get("transactions", [])
        for tx in transactions:
            from_entity = tx.get("from")
            to_entity = tx.get("to")
            if from_entity and len(from_entity) > 2:
                # Check if it looks like a company
                entity_type = "company" if self._looks_like_company(from_entity) else "person"
                entities.append({
                    "type": entity_type,
                    "name": from_entity,
                    "confidence": 0.9,
                    "source": "transaction_from",
                })
            if to_entity and len(to_entity) > 2:
                entity_type = "company" if self._looks_like_company(to_entity) else "person"
                entities.append({
                    "type": entity_type,
                    "name": to_entity,
                    "confidence": 0.9,
                    "source": "transaction_to",
                })
        
        return self._deduplicate_entities(entities)
    
    def extract_from_event(self, event: Dict[str, Any]) -> List[Dict]:
        """Extract entities from a single event."""
        entities = []
        data = event.get("data", {})
        event_type = event.get("event_type", "")
        
        # Extract based on event type
        if event_type == "case_created":
            # Extract from title (but filter out noise)
            title = data.get("title", "")
            if title and not self._is_case_title_noise(title):
                # Only add if it looks like a real entity
                if self._looks_like_person_name(title):
                    entities.append({
                        "type": "person",
                        "name": title,
                        "confidence": 0.6,
                        "source": "case_title",
                    })
        
        elif event_type == "case_updated":
            # Check for metadata updates
            changes = data.get("changes", {})
            metadata_change = changes.get("case_metadata", {}).get("new", {})
            if metadata_change:
                entities.extend(self.extract_from_case_metadata(metadata_change))
        
        return self._deduplicate_entities(entities)
    
    def _looks_like_company(self, text: str) -> bool:
        """Check if text looks like a company name."""
        for pattern in self.COMPANY_PATTERNS:
            if re.match(pattern, text):
                return True
        # Check for common company suffixes
        text_lower = text.lower()
        company_suffixes = ['pt', 'cv', 'persero', 'tbk', 'ltd', 'inc']
        for suffix in company_suffixes:
            if text_lower.endswith(suffix) or f" {suffix}" in text_lower:
                return True
        return False
    
    def _looks_like_person_name(self, text: str) -> bool:
        """Check if text looks like a person name (2-3 words, capitalized)."""
        words = text.split()
        if len(words) not in [2, 3]:
            return False
        # Check if each word starts with capital letter
        for word in words:
            if not word[0].isupper():
                return False
        # Reject common non-person phrases
        noise_words = {'test', 'case', 'investigation', 'money', 'laundering', 'triangle'}
        text_lower = text.lower()
        for noise in noise_words:
            if noise in text_lower:
                return False
        return True
    
    def _is_case_title_noise(self, title: str) -> bool:
        """Check if case title is noise (not a real entity)."""
        noise_patterns = [
            r'(?i)test',
            r'(?i)investigation',
            r'(?i)money\s+laundering',
            r'(?i)triangle',
            r'(?i)circular',
            r'(?i)suspicious',
        ]
        for pattern in noise_patterns:
            if re.search(pattern, title):
                return True
        return False
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities by name and type."""
        seen = set()
        unique = []
        for e in entities:
            key = f"{e['type']}:{e['name']}"
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique