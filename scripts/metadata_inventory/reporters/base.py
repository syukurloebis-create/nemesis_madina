# scripts/metadata_inventory/reporters/base.py
class BaseReporter(ABC):
    """Base reporter dengan manifest version."""
    
    REPORTER_API_VERSION = "1.0"
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def version(self) -> str: ...
    
    @property
    def supports(self) -> List[str]:
        """Format yang didukung: snapshot, diff, baseline"""
        return ["snapshot"]
    
    def validate(self):
        """Validasi reporter API compatibility."""
        # Implementation