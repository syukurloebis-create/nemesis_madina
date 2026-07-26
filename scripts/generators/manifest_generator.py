# scripts/generators/manifest_generator.py
from typing import Dict, Any
from datetime import datetime
import json
import yaml
import subprocess
from scripts.architecture.models.module import Module
from scripts.inventory.query import InventoryQuery
from scripts.architecture.logging.logger import NemesisLogger

class ManifestGenerator:
    def __init__(self, inventory: InventoryQuery):
        self.inventory = inventory
        self.logger = NemesisLogger()
        self.manifest: Dict[str, Any] = {}
    
    def generate(self) -> Dict[str, Any]:
        """Generate repository manifest"""
        modules = self.inventory.storage.get_modules()
        
        self.manifest = {
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'repository': {
                'name': 'NEMESIS-Madina',
                'git_commit': self._get_git_commit(),
                'git_branch': self._get_git_branch(),
            },
            'inventory': {
                'total_modules': len(modules),
                'modules_by_type': self._group_by_type(modules),
                'modules_by_language': self._group_by_language(modules),
            },
            'legacy': {
                'total_legacy_imports': len(self.inventory.get_legacy_imports())
            }
        }
        
        self.logger.info(f"Manifest generated: {self.manifest['inventory']['total_modules']} modules")
        return self.manifest
    
    def save(self, output_path: str = 'docs/architecture/generated/manifest.yaml'):
        """Save manifest to file"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(self.manifest, f)
        
        self.logger.info(f"Manifest saved to {output_path}")
    
    def _get_git_commit(self) -> str:
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return 'unknown'
    
    def _get_git_branch(self) -> str:
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return 'unknown'
    
    def _group_by_type(self, modules: list) -> Dict[str, int]:
        result = {}
        for module in modules:
            module_type = module.get('type', 'unknown')
            result[module_type] = result.get(module_type, 0) + 1
        return result
    
    def _group_by_language(self, modules: list) -> Dict[str, int]:
        result = {}
        for module in modules:
            language = module.get('language', 'unknown')
            result[language] = result.get(language, 0) + 1
        return result