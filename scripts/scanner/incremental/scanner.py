# scripts/scanner/incremental/scanner.py
from pathlib import Path
from typing import List, Dict, Any
from scripts.scanner.core.plugin_manager import PluginManager
from scripts.scanner.incremental.cache import IncrementalCache
from scripts.architecture.logging.logger import NemesisLogger

class IncrementalScanner:
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        self.cache = IncrementalCache()
        self.logger = NemesisLogger()
        self.results: List[Dict[str, Any]] = []
    
    def scan_changed(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan only changed files"""
        changed_files = self.cache.get_changed_files(directory)
        
        if not changed_files:
            self.logger.info("No changed files found")
            return self.results
        
        self.logger.info(f"Scanning {len(changed_files)} changed files")
        
        for filepath in changed_files:
            plugin = self.plugin_manager.get_plugin_for_file(filepath)
            if plugin:
                result = plugin.scan_file(filepath)
                if result:
                    self.results.append(result)
                    self.cache.mark_scanned(filepath)
        
        self.cache.save()
        self.logger.info(f"Scan complete. Found {len(self.results)} modules.")
        return self.results
    
    def scan_all(self, directory: Path) -> List[Dict[str, Any]]:
        """Full scan of all files"""
        self.logger.info("Performing full scan")
        
        for filepath in directory.rglob('*.py'):
            plugin = self.plugin_manager.get_plugin_for_file(filepath)
            if plugin:
                result = plugin.scan_file(filepath)
                if result:
                    self.results.append(result)
                    self.cache.mark_scanned(filepath)
        
        self.cache.save()
        self.logger.info(f"Full scan complete. Found {len(self.results)} modules.")
        return self.results
    
    def get_results(self) -> List[Dict[str, Any]]:
        return self.results