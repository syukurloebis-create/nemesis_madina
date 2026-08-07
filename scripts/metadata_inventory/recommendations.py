# scripts/metadata_inventory/recommendations.py
from typing import Dict, List, Optional, Any
from .dtos import Finding, FindingID


class RecommendationEngine:
    """Policy-based recommendation engine (menghasilkan Recommendation terpisah)."""

    
    def __init__(self, mode: str = "enterprise"):
        self.mode = mode
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[FindingID, str]:
        """Load policies based on mode."""
        base_policies = {
            FindingID.ORM001: "Consider consolidating to single metadata or configure Alembic for multiple targets",
            FindingID.ORM002: "Resolve duplicate table naming to avoid ambiguity",
            FindingID.ORM003: "Consolidate metadata to resolve cross-metadata foreign key violation",
            FindingID.ORM004: "Update Alembic target_metadata to match actual metadata",
            FindingID.ORM005: "Ensure all models use consistent registry",
            FindingID.ORM006: "Remove empty Base or add models to it",
            FindingID.ORM007: "Consolidate metadata to resolve cross-metadata relationship",
            FindingID.ORM008: "Update bootstrap import to include all model modules",
            FindingID.ORM009: "Resolve duplicate model naming",
            FindingID.ORM010: "Configure Alembic target_metadata in env.py",
        }
        
        if self.mode == "strict":
            # More aggressive recommendations
            base_policies[FindingID.ORM001] = "MANDATORY: Consolidate to single metadata"
            base_policies[FindingID.ORM003] = "MANDATORY: Resolve cross-metadata FK"
        
        return base_policies
    
    
    def recommend(self, findings: List[Finding]) -> List[Recommendation]:
        """Generate recommendations dari findings."""
        recommendations = []
        
        for finding in findings:
            policy = self.policies.get(finding.id)
            if policy:
                recommendations.append(Recommendation(
                    finding_id=finding.id,
                    policy_mode=self.mode,
                    recommendation=policy["text"],
                    documentation_url=policy.get("url")
                ))
            else:
                recommendations.append(Recommendation(
                    finding_id=finding.id,
                    policy_mode=self.mode,
                    recommendation="Manual review required"
                ))
        
        return recommendations

@dataclass(frozen=True)
class Recommendation:
    """Recommendation tanpa text hardcoded."""
    finding_id: FindingID
    policy_mode: str
    policy_version: str
    documentation: Optional[str] = None

@dataclass(frozen=True)
class PolicyDefinition:
    text: str
    documentation: Optional[str] = None
    severity_override: Optional[Severity] = None

class RecommendationRegistry:
    """Registry untuk recommendation policies."""
    
    def __init__(self):
        self._policies = self._load_registry()
    
    def get_recommendation(self, finding_id: FindingID, mode: str) -> Recommendation:
        """Get recommendation tanpa text hardcoded."""
        policy = self._policies.get(mode, {}).get(finding_id.value)
        if not policy:
            return Recommendation(
                finding_id=finding_id,
                policy_mode=mode,
                policy_version="1.0",
                documentation=None
            )
        
        return Recommendation(
            finding_id=finding_id,
            policy_mode=mode,
            policy_version="1.0",
            documentation=policy.get("documentation")
        )
    
    def get_text(self, finding_id: FindingID, mode: str) -> str:
        """Get recommendation text from registry."""
        policy = self._policies.get(mode, {}).get(finding_id.value)
        return policy.get("text", "Manual review required") if policy else "Manual review required"