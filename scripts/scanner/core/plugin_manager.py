# scripts/scanner/core/plugin_manager.py
from typing import Dict, List, Optional
from pathlib import Path
from scripts.architecture.interfaces.i_scanner_plugin import IScannerPlugin
from scripts.architecture.logging.logger import NemesisLogger

class PluginManager:
    def __init__(self):
        self.logger = NemesisLogger()
        self.plugins: Dict[str, IScannerPlugin] = {}
        self.extensions: Dict[str, IScannerPlugin] = {}
    
    def register(self, plugin: IScannerPlugin) -> None:
        """Register a scanner plugin"""
        self.plugins[plugin.name] = plugin
        for ext in plugin.extensions:
            self.extensions[ext] = plugin
        self.logger.info(f"Registered plugin: {plugin.name}", 
                        extensions=plugin.extensions)
    
    def get_plugin_for_file(self, filepath: Path) -> Optional[IScannerPlugin]:
        """Get plugin for a file extension"""
        ext = filepath.suffix.lower()
        return self.extensions.get(ext)
    
    def get_all_plugins(self) -> List[IScannerPlugin]:
        """Get all registered plugins"""
        return list(self.plugins.values())