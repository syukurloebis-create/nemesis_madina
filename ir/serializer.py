# ir/serializer.py

import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime


class CanonicalSerializer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_table(self, name: str, data: Any, schema_version: str) -> None:
        """Write a table with deterministic formatting"""
        # Determine if data is a list or dict
        if isinstance(data, list):
            # Sort by primary key if available
            if data and hasattr(data[0], 'id'):
                data = sorted(data, key=lambda x: x.id)
            # Convert to dict with metadata
            output = {
                "schema_version": schema_version,
                "table": name,
                "rows": [self._to_dict(item) for item in data]
            }
        else:
            output = {
                "schema_version": schema_version,
                "table": name,
                "data": data
            }
        
        file_path = self.output_dir / f"{name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                output,
                f,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                default=self._json_default
            )
        # Ensure LF newline
        with open(file_path, 'rb') as f:
            content = f.read()
        if content and not content.endswith(b'\n'):
            with open(file_path, 'wb') as f:
                f.write(content + b'\n')
    
    def _to_dict(self, obj) -> Dict:
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj
    
    def _json_default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

Serializer = CanonicalSerializer