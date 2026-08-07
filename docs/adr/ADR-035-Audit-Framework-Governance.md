# \# ADR-035: Audit Framework Governance (Amandemen)

# 

# \## Evolution Policy

# 

# \### Frozen Contracts (Require ADR)

# \- Collector → RawCollection

# \- RawCollection → Normalizer

# \- DTOs (all @dataclass(frozen=True))

# \- AuditResult

# \- AuditResultBuilder

# \- FindingID enum

# \- Finding Registry YAML schema

# \- Plugin API version

# \- Reporter API (Visitor pattern)

# \- PipelineContext

# 

# \### Versioned Components (Can Evolve)

# \- Recommendation policies (via recommendation\_registry.yaml)

# \- Health-score formula (via weights.yaml)

# \- Weight configurations (via weights.yaml)

# \- Diff heuristics (via diff engine version)

# \- Fingerprint algorithm (with versioned output)

# \- Report formats (JSON/Markdown/SARIF versions)

# 

# \### Versioning Strategy

# \- Registry: semantic version (e.g., 1.2.0)

# \- Framework: semantic version (e.g., 1.0.0)

# \- Schema: semantic version (e.g., 1.0)

# \- Plugin API: semantic version (e.g., 1.0)

# 

# \### Change Process

# 1\. Frozen contracts: New ADR required

# 2\. Versioned components: Increment version, document changes

# 3\. Deprecation: 2-release deprecation period

# 4\. Migration: Schema migration path for each version

