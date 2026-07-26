# scripts/architecture/models/manifest.py
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Manifest:
    """Repository manifest"""
    version: str
    timestamp: datetime
    git_commit: str
    git_branch: str
    total_modules: int
    modules_by_type: Dict[str, int]
    modules_by_language: Dict[str, int]
    legacy_imports: int
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'git_commit': self.git_commit,
            'git_branch': self.git_branch,
            'total_modules': self.total_modules,
            'modules_by_type': self.modules_by_type,
            'modules_by_language': self.modules_by_language,
            'legacy_imports': self.legacy_imports,
            'checksum': self.checksum
        }