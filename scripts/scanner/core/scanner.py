# scripts/scanner/core/scanner.py
from pathlib import Path
from typing import List, Dict, Any, Optional 
from scripts.scanner.core.plugin_manager import PluginManager
from scripts.architecture.logging.logger import NemesisLogger

class Scanner:
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        self.logger = NemesisLogger()
        self.results: List[Dict[str, Any]] = []
    
    def scan_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Scan a single file"""
        plugin = self.plugin_manager.get_plugin_for_file(filepath)
        if plugin:
            self.logger.debug(f"Scanning file: {filepath}", plugin=plugin.name)
            result = plugin.scan_file(filepath)
            if result:
                self.results.append(result)
            return result
        return None
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """Scan all files in a directory"""
        self.logger.info(f"Starting scan of directory: {directory}")
        
        pattern = "**/*" if recursive else "*"
        for filepath in directory.glob(pattern):
            if filepath.is_file():
                self.scan_file(filepath)
        
        self.logger.info(f"Scan complete. Found {len(self.results)} modules.")
        return self.results
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get scan results"""
        return self.results