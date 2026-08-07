# scripts/metadata_inventory/plugins/loader.py
import yaml
from pathlib import Path
from typing import Dict, Any

class PluginLoader:
    """Load plugin dengan manifest."""
    PLUGIN_API_VERSION = "1.0"
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
    
    def load_all(self) -> Dict[str, Any]:
        """Load semua plugin dengan validasi manifest."""
        plugins = {}
        
        for manifest_path in self.plugin_dir.glob("*_plugin.yaml"):
            with open(manifest_path, "r") as f:
                manifest = yaml.safe_load(f)

            plugin_api = manifest.get("plugin_api")
            if plugin_api != self.PLUGIN_API_VERSION:
                print(f"⚠️ Plugin {manifest['name']} requires API {plugin_api}, "
                      f"but framework supports {self.PLUGIN_API_VERSION}")
                continue
            
            # Load plugin class
            module_name = manifest_path.stem
            module = importlib.import_module(f"metadata_inventory.plugins.{module_name}")
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and 
                    issubclass(attr, AuditPlugin) and 
                    attr != AuditPlugin):
                    plugins[manifest["name"]] = {
                        "instance": attr(),
                        "manifest": manifest
                    }
        
        return plugins