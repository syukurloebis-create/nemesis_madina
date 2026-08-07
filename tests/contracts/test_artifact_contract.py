# tests/contracts/test_artifact_contract.py (Fixed with traceback)
import sys
import json
import traceback
from pathlib import Path
from typing import Any, Type

# Add scripts to path FIRST
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest

from metadata_inventory.discovery.import_runtime import ImportArtifact
from metadata_inventory.discovery.discovery_artifact import RegistryArtifact, DiscoveryArtifact
from metadata_inventory.verification.result import VerificationResult

pytestmark = pytest.mark.metadata_inventory


class ArtifactContract:
    """Base contract for all artifacts."""

    @staticmethod
    def verify_to_payload(artifact: Any) -> bool:
        """Verify to_payload returns a dict."""
        payload = artifact.to_payload()
        return isinstance(payload, dict)

    @staticmethod
    def verify_from_payload(cls: Type, payload: dict) -> bool:
        """Verify from_payload reconstructs artifact."""
        artifact = cls.from_payload(payload)
        return artifact is not None

    @staticmethod
    def verify_roundtrip(artifact: Any) -> bool:
        """Verify to_payload -> from_payload preserves artifact."""
        payload = artifact.to_payload()
        reconstructed = type(artifact).from_payload(payload)

        if hasattr(artifact, 'fingerprint') and hasattr(reconstructed, 'fingerprint'):
            return artifact.fingerprint == reconstructed.fingerprint
        return True

    @staticmethod
    def verify_json_serializable(artifact: Any) -> bool:
        """
        Verify artifact is JSON serializable.
        
        Raises exception with full traceback if serialization fails.
        """
        print(f"\n=== DEBUG: verify_json_serializable ===")
        print(f"Artifact type: {type(artifact)}")
        
        payload = artifact.to_payload()
        print(f"Payload type: {type(payload)}")
        if isinstance(payload, dict):
            print(f"Payload keys: {list(payload.keys())}")
        
        print("Serializing with json.dumps(payload)...")
        json.dumps(payload)
        print("SUCCESS!")
        return True


class TestArtifactContract:
    """Test all artifacts satisfy the contract."""

    def test_import_artifact_contract(self, sample_import_artifact):
        """Test ImportArtifact satisfies contract."""
        artifact = sample_import_artifact

        assert ArtifactContract.verify_to_payload(artifact)
        assert ArtifactContract.verify_from_payload(ImportArtifact, artifact.to_payload())
        assert ArtifactContract.verify_roundtrip(artifact)
        assert ArtifactContract.verify_json_serializable(artifact)

    def test_registry_artifact_contract(self, sample_registry_artifact):
        """Test RegistryArtifact satisfies contract."""
        artifact = sample_registry_artifact

        assert ArtifactContract.verify_to_payload(artifact)
        assert ArtifactContract.verify_from_payload(RegistryArtifact, artifact.to_payload())
        assert ArtifactContract.verify_roundtrip(artifact)
        assert ArtifactContract.verify_json_serializable(artifact)

    def test_discovery_artifact_contract(self, sample_artifact):
        """Test DiscoveryArtifact satisfies contract."""
        artifact = sample_artifact

        assert ArtifactContract.verify_to_payload(artifact)
        assert ArtifactContract.verify_from_payload(DiscoveryArtifact, artifact.to_payload())
        assert ArtifactContract.verify_roundtrip(artifact)
        assert ArtifactContract.verify_json_serializable(artifact)

    def test_verification_result_contract(self, sample_verification_result):
        """Test VerificationResult satisfies contract."""
        result = sample_verification_result

        assert ArtifactContract.verify_to_payload(result)
        assert ArtifactContract.verify_from_payload(VerificationResult, result.to_payload())
        assert ArtifactContract.verify_roundtrip(result)
        assert ArtifactContract.verify_json_serializable(result)