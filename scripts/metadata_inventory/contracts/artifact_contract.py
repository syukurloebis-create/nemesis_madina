# scripts/metadata_inventory/contracts/artifact_contract.py
"""
Artifact Contract - Definisi Fingerprint vs Checksum.
"""

from typing import Dict, Any, List
from dataclasses import dataclass, is_dataclass, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import json


@dataclass(frozen=True)
class ArtifactContract:
    """
    Kontrak untuk Artifact Identity vs Integrity.
    """

    FINGERPRINT_SCOPE = [
        "registry.tables",
        "registry.models",
        "registry.relationships",
        "import.mappers",
        "schema.structure"
    ]

    CHECKSUM_SCOPE = [
        "FINGERPRINT_SCOPE",
        "timestamp",
        "producer",
        "artifact_id",
        "schema_version",
        "metadata"
    ]

    @staticmethod
    def is_fingerprint_stable(fingerprint1: str, fingerprint2: str) -> bool:
        """Check if two fingerprints represent the same artifact identity."""
        return fingerprint1 == fingerprint2

    @staticmethod
    def is_checksum_valid(checksum: str, payload: Dict[str, Any]) -> bool:
        """Verify checksum against payload."""
        from ..canonical_serializer import Fingerprint
        expected = Fingerprint.generate({"payload": payload})
        return checksum == expected

    @staticmethod
    def _normalize(obj: Any) -> Any:
        """Recursively normalize object to JSON serializable."""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if is_dataclass(obj):
            return ArtifactContract._normalize(asdict(obj))
        if isinstance(obj, (tuple, list)):
            return [ArtifactContract._normalize(item) for item in obj]
        if isinstance(obj, dict):
            return {str(k): ArtifactContract._normalize(v) for k, v in obj.items()}
        if hasattr(obj, '__dict__'):
            return ArtifactContract._normalize(obj.__dict__)
        return str(obj)

    @staticmethod
    def _scan_non_serializable(obj: Any, path: str = "root") -> None:
        """Scan for non-JSON-serializable objects."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                ArtifactContract._scan_non_serializable(v, f"{path}.{k}")
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                ArtifactContract._scan_non_serializable(v, f"{path}[{i}]")
        else:
            if not isinstance(obj, (str, int, float, bool, type(None))):
                print(f"NON-SERIALIZABLE: {path} -> {type(obj)} -> {repr(obj)[:100]}")

    @staticmethod
    def verify_json_serializable(artifact: Any) -> bool:
        """Verify artifact is JSON serializable."""
        import json
        import traceback
        
        # RAISE ERROR TO CONFIRM THIS FUNCTION IS CALLED
        raise RuntimeError("VERIFY_JSON_SERIALIZABLE CALLED - This function is being used by pytest")
        
        try:
            if hasattr(artifact, 'to_payload'):
                payload = artifact.to_payload()
            elif is_dataclass(artifact):
                payload = asdict(artifact)
            elif hasattr(artifact, '__dict__'):
                payload = {
                    k: v for k, v in artifact.__dict__.items()
                    if not k.startswith('_')
                }
            else:
                payload = str(artifact)

            normalized = ArtifactContract._normalize(payload)
            json.dumps(normalized)
            return True
        except Exception:
            return False