# scripts/generators/manifest/provenance.py
@dataclass
class ProvenanceStep:
    """Single step in provenance chain"""
    component: str
    version: str
    input_hash: str
    output_hash: str
    timestamp: datetime
    duration: float
    metadata: Dict[str, Any] = None

@dataclass
class Provenance:
    """Complete provenance chain"""
    git_commit: str
    git_branch: str
    git_tag: Optional[str]
    
    scanner_version: str
    scanner_hash: str
    
    normalizer_version: str
    normalizer_hash: str
    
    inventory_version: str
    inventory_hash: str
    inventory_schema_version: int
    
    rules_version: str
    rules_hash: str
    
    generator_version: str
    generator_hash: str
    
    manifest_version: str
    manifest_hash: str
    
    artifacts: Dict[str, str]  # path -> checksum
    
    def get_chain(self) -> List[ProvenanceStep]:
        """Get provenance chain as list"""
        return [
            ProvenanceStep(
                component='scanner',
                version=self.scanner_version,
                input_hash=self.git_commit,
                output_hash=self.scanner_hash,
                timestamp=datetime.now(),
                duration=0
            ),
            # ... etc
        ]
    
    def verify(self) -> bool:
        """Verify provenance chain"""
        # Check if chain is consistent
        # Check if hashes match
        # Check if versions are compatible
        pass

# Manifest Generator with Provenance
class ManifestGenerator:
    def generate(self):
        provenance = Provenance(
            git_commit=self._get_git_commit(),
            git_branch=self._get_git_branch(),
            git_tag=self._get_git_tag(),
            scanner_version=VersionManager.SCANNER_VERSION,
            scanner_hash=self._calculate_scanner_hash(),
            normalizer_version=VersionManager.NORMALIZER_VERSION,
            normalizer_hash=self._calculate_normalizer_hash(),
            inventory_version=VersionManager.INVENTORY_VERSION,
            inventory_hash=self._calculate_inventory_hash(),
            inventory_schema_version=VersionManager.SCHEMA_VERSION,
            rules_version=VersionManager.RULES_VERSION,
            rules_hash=self._calculate_rules_hash(),
            generator_version=VersionManager.GENERATOR_VERSION,
            generator_hash=self._calculate_generator_hash(),
            manifest_version=VersionManager.MANIFEST_VERSION,
            manifest_hash=self._calculate_manifest_hash(),
            artifacts=self._get_artifact_checksums()
        )
        
        manifest = {
            'version': VersionManager.MANIFEST_VERSION,
            'build': {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'duration': self._get_duration(),
            },
            'provenance': provenance.__dict__,
            'inventory': self._get_inventory_summary(),
            'validation': self._get_validation_summary(),
            'artifacts': provenance.artifacts,
            'checksum': self._calculate_final_checksum(provenance)
        }
        
        return manifest