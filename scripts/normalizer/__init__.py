# scripts/normalizer/__init__.py
from typing import Dict, Any, List, Optional
from scripts.architecture.models.module import Module, ModuleType, Language
from scripts.architecture.models.relation import Relation
from scripts.architecture.models import Metric
from scripts.architecture.logging.logger import NemesisLogger

class Normalizer:
    def __init__(self):
        self.logger = NemesisLogger()
        self.modules: List[Module] = []
        self.relations: List[Relation] = []
        self.metrics: List[Metric] = []
    
    def normalize_module(self, raw: Dict[str, Any]) -> Optional[Module]:
        """Normalize raw module data"""
        try:
            # Validate required fields
            required = ['id', 'name', 'path', 'type', 'language']
            for field in required:
                if field not in raw:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert to enum
            module_type = ModuleType(raw['type'])
            language = Language(raw['language'])
            
            # Create module
            module = Module(
                id=raw['id'],
                name=raw['name'],
                path=raw['path'],
                type=module_type,
                language=language,
                lines=raw.get('lines', 0),
                complexity=raw.get('complexity', 0),
                imports=raw.get('imports', []),
                classes=raw.get('classes', []),
                functions=raw.get('functions', []),
                test_coverage=raw.get('test_coverage', None),
                deprecated=raw.get('deprecated', False)
            )
            
            return module
            
        except Exception as e:
            self.logger.error(f"Normalization failed for {raw.get('path')}", error=str(e))
            return None
    
    def normalize_relation(self, source: str, target: str, rel_type: str) -> Relation:
        """Create a normalized relation"""
        return Relation(source=source, target=target, type=rel_type)
    
    def extract_relations(self, module: Module) -> List[Relation]:
        """Extract relations from module"""
        relations = []
        for import_name in module.imports:
            relations.append(Relation(
                source=module.id,
                target=import_name,
                type='imports'
            ))
        return relations
    
    def normalize_all(self, raw_modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize all modules"""
        self.logger.info(f"Normalizing {len(raw_modules)} modules")
        
        for raw in raw_modules:
            module = self.normalize_module(raw)
            if module:
                self.modules.append(module)
                # Extract relations
                relations = self.extract_relations(module)
                self.relations.extend(relations)
        
        self.logger.info(f"Normalized {len(self.modules)} modules, {len(self.relations)} relations")
        
        return {
            'modules': self.modules,
            'relations': self.relations
        }
    
    def get_modules(self) -> List[Module]:
        return self.modules
    
    def get_relations(self) -> List[Relation]:
        return self.relations