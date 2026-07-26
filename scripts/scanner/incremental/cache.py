# scripts/scanner/incremental/cache.py
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from scripts.architecture.logging.logger import NemesisLogger

class IncrementalCache:
    def __init__(self, cache_dir: Path = Path('.scanner-cache')):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / 'file_hashes.json'
        self.logger = NemesisLogger()
        self.hashes: Dict[str, str] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                self.hashes = json.load(f)
    
    def _save_cache(self) -> None:
        with open(self.cache_file, 'w') as f:
            json.dump(self.hashes, f, indent=2)
    
    def get_file_hash(self, filepath: Path) -> str:
        """Calculate SHA-256 hash of file"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def has_changed(self, filepath: Path) -> bool:
        """Check if file has changed since last scan"""
        current_hash = self.get_file_hash(filepath)
        previous_hash = self.hashes.get(str(filepath))
        return current_hash != previous_hash
    
    def mark_scanned(self, filepath: Path) -> None:
        """Mark file as scanned"""
        self.hashes[str(filepath)] = self.get_file_hash(filepath)
    
    def get_changed_files(self, directory: Path) -> List[Path]:
        """Get all changed files in directory"""
        changed = []
        for filepath in directory.rglob('*.py'):
            if self.has_changed(filepath):
                changed.append(filepath)
        return changed
    
    def save(self) -> None:
        """Save cache to disk"""
        self._save_cache()
        self.logger.info(f"Cache saved: {len(self.hashes)} files")