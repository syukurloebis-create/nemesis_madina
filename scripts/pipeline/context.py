# scripts/pipeline/context.py

class StageContext:
    """Base class for stage contexts"""
    
    def __init__(self, parent: 'ArchitectureContext' = None):
        self.parent = parent
        self._data = {}
        self._metadata = {}
    
    def set(self, key: str, value: Any):
        """Set data in context"""
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get data from context (check parent if not found)"""
        if key in self._data:
            return self._data[key]
        if self.parent:
            return self.parent.get(key, default)
        return default
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata"""
        self._metadata[key] = value
    
    def get_metadata(self, key: str) -> Any:
        """Get metadata"""
        return self._metadata.get(key)

class ScannerContext(StageContext):
    """Scanner-specific context"""
    
    @property
    def raw_modules(self) -> List[Dict]:
        return self.get('raw_modules', [])
    
    @raw_modules.setter
    def raw_modules(self, value):
        self.set('raw_modules', value)
    
    @property
    def scan_stats(self) -> Dict:
        return self.get('scan_stats', {})
    
    @scan_stats.setter
    def scan_stats(self, value):
        self.set('scan_stats', value)

class NormalizerContext(StageContext):
    """Normalizer-specific context"""
    
    @property
    def normalized_modules(self) -> List[Dict]:
        return self.get('normalized_modules', [])
    
    @normalized_modules.setter
    def normalized_modules(self, value):
        self.set('normalized_modules', value)

class InventoryContext(StageContext):
    """Inventory-specific context"""
    
    @property
    def inventory_db(self) -> Any:
        return self.get('inventory_db')
    
    @inventory_db.setter
    def inventory_db(self, value):
        self.set('inventory_db', value)

class RuleContext(StageContext):
    """Rule engine context"""
    
    @property
    def violations(self) -> List[Dict]:
        return self.get('violations', [])
    
    @violations.setter
    def violations(self, value):
        self.set('violations', value)

class GeneratorContext(StageContext):
    """Generator context"""
    
    @property
    def artifacts(self) -> Dict[str, Any]:
        return self.get('artifacts', {})
    
    @artifacts.setter
    def artifacts(self, value):
        self.set('artifacts', value)

class ArchitectureContext:
    """Top-level context with hierarchical stages"""
    
    def __init__(self):
        self.scanner = ScannerContext(self)
        self.normalizer = NormalizerContext(self)
        self.inventory = InventoryContext(self)
        self.rules = RuleContext(self)
        self.generators = GeneratorContext(self)
        
        self._shared_data = {}
        self.state = ArchitectureState.BOOTSTRAPPED
        self.metrics = {}
        self.config = {}
        self.log = None
        self.event_bus = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get shared data"""
        return self._shared_data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set shared data"""
        self._shared_data[key] = value
    
    def to_json(self) -> Dict:
        """Export to JSON"""
        return {
            'state': self.state.value,
            'metrics': self.metrics,
            'shared': self._shared_data,
            'scanner': self.scanner._data,
            'normalizer': self.normalizer._data,
            'inventory': self.inventory._data,
            'rules': self.rules._data,
            'generators': self.generators._data,
        }