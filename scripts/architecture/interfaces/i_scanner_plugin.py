# scripts/architecture/interfaces/i_scanner_plugin.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

class IScannerPlugin(ABC):
    """Interface for scanner plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def extensions(self) -> List[str]:
        """File extensions this plugin handles"""
        pass
    
    @abstractmethod
    def scan_file(self, filepath: Path) -> Dict[str, Any]:
        """Scan a single file and return raw data"""
        pass
    
    @abstractmethod
    def scan_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan all files in a directory"""
        pass