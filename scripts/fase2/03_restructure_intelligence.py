#!/usr/bin/env python3
"""
NEMESIS FASE 2 - Restructure Intelligence Layer
Memisahkan ML, Legal, dan Explainability components
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

INTEL_DIR = PROJECT_ROOT / "backend" / "intelligence"
ML_DIR = INTEL_DIR / "ml"
LEGAL_DIR = INTEL_DIR / "legal"
EXPLAIN_DIR = INTEL_DIR / "explainability"

def create_intel_structure():
    """Buat struktur intelligence yang terorganisir"""
    print("\n[DIR] Creating intelligence structure...")
    
    ML_DIR.mkdir(parents=True, exist_ok=True)
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    EXPLAIN_DIR.mkdir(parents=True, exist_ok=True)
    
    return True

def create_ml_modules():
    """Buat ML modules"""
    
    # __init__.py
    init_content = '''"""
NEMESIS ML Module - Machine Learning Capabilities
"""

from backend.intelligence.ml.anomaly import AnomalyDetector
from backend.intelligence.ml.scoring import RiskScorer
from backend.intelligence.ml.calibration import ConfidenceCalibrator

__all__ = [
    'AnomalyDetector',
    'RiskScorer',
    'ConfidenceCalibrator'
]
'''
    (ML_DIR / "__init__.py").write_text(init_content)
    print("  [OK] Created: ml/__init__.py")
    
    # anomaly.py
    anomaly_content = '''"""
Anomaly Detection Module
"""

from typing import List, Dict, Any, Optional
import numpy as np


class AnomalyDetector:
    """Detect anomalies in data"""
    
    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
    
    def detect(self, data: List[float]) -> List[int]:
        """Detect anomalies in time series data"""
        if not data:
            return []
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs(value - mean) / std
            if z_score > 3:  # 3-sigma rule
                anomalies.append(i)
        
        return anomalies
    
    def get_anomaly_score(self, value: float, historical: List[float]) -> float:
        """Get anomaly score for a single value"""
        if not historical:
            return 0.0
        
        mean = np.mean(historical)
        std = np.std(historical)
        
        if std == 0:
            return 0.0
        
        z_score = abs(value - mean) / std
        return min(z_score / 5, 1.0)  # Normalize to [0,1]
'''
    (ML_DIR / "anomaly.py").write_text(anomaly_content)
    print("  [OK] Created: ml/anomaly.py")
    
    # scoring.py
    scoring_content = '''"""
Risk Scoring Module
"""

from typing import Dict, Any, List, Optional


class RiskScorer:
    """Compute risk scores"""
    
    def __init__(self):
        self.weights = {
            "anomaly_score": 0.3,
            "collusion_risk": 0.25,
            "historical_risk": 0.2,
            "velocity": 0.15,
            "volume": 0.1
        }
    
    def compute_score(self, features: Dict[str, float]) -> float:
        """Compute weighted risk score"""
        score = 0.0
        total_weight = 0.0
        
        for feature, weight in self.weights.items():
            if feature in features:
                score += features[feature] * weight
                total_weight += weight
        
        if total_weight > 0:
            score /= total_weight
        
        return min(max(score, 0.0), 1.0)
    
    def get_severity(self, score: float) -> str:
        """Get severity level from score"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "info"
    
    def get_recommendation(self, score: float, features: Dict[str, float]) -> str:
        """Get action recommendation based on score"""
        if score >= 0.8:
            return "Immediate investigation required"
        elif score >= 0.6:
            return "Escalate for review"
        elif score >= 0.4:
            return "Monitor closely"
        else:
            return "No action needed"
'''
    (ML_DIR / "scoring.py").write_text(scoring_content)
    print("  [OK] Created: ml/scoring.py")
    
    # calibration.py
    calibration_content = '''"""
Confidence Calibration Module
"""

from typing import List, Dict, Any
import numpy as np


class ConfidenceCalibrator:
    """Calibrate model confidence scores"""
    
    def __init__(self):
        self.calibration_data: List[tuple] = []  # (predicted, actual)
    
    def add_calibration_point(self, predicted_score: float, actual_outcome: bool):
        """Add calibration data point"""
        self.calibration_data.append((predicted_score, actual_outcome))
    
    def calibrate(self, raw_score: float) -> float:
        """Calibrate raw confidence score"""
        if len(self.calibration_data) < 10:
            return raw_score
        
        # Simple Platt scaling (simplified)
        predicted = [p for p, _ in self.calibration_data]
        actual = [a for _, a in self.calibration_data]
        
        if not predicted:
            return raw_score
        
        # Compute calibration factor
        avg_predicted = np.mean(predicted)
        avg_actual = np.mean(actual)
        
        if avg_predicted > 0:
            factor = avg_actual / avg_predicted
        else:
            factor = 1.0
        
        calibrated = raw_score * factor
        return min(max(calibrated, 0.0), 1.0)
    
    def get_calibration_metrics(self) -> Dict[str, Any]:
        """Get calibration performance metrics"""
        if not self.calibration_data:
            return {"status": "insufficient_data"}
        
        predicted = [p for p, _ in self.calibration_data]
        actual = [a for _, a in self.calibration_data]
        
        return {
            "mean_predicted": float(np.mean(predicted)),
            "mean_actual": float(np.mean(actual)),
            "calibration_points": len(self.calibration_data),
            "brier_score": float(np.mean([(p - a) ** 2 for p, a in self.calibration_data]))
        }
'''
    (ML_DIR / "calibration.py").write_text(calibration_content)
    print("  [OK] Created: ml/calibration.py")
    
    return True

def create_legal_modules():
    """Buat Legal modules"""
    
    # __init__.py
    init_content = '''"""
NEMESIS Legal Module - Legal Compliance & Audit
"""

from backend.intelligence.legal.audit import AuditTrailValidator
from backend.intelligence.legal.compliance import ComplianceChecker
from backend.intelligence.legal.report import LegalReportGenerator

__all__ = [
    'AuditTrailValidator',
    'ComplianceChecker',
    'LegalReportGenerator'
]
'''
    (LEGAL_DIR / "__init__.py").write_text(init_content)
    print("  [OK] Created: legal/__init__.py")
    
    # audit.py
    audit_content = '''"""
Audit Trail Validator
"""

from typing import List, Dict, Any
from datetime import datetime


class AuditTrailValidator:
    """Validate audit trail integrity"""
    
    def __init__(self):
        self.audit_entries: List[Dict[str, Any]] = []
    
    def add_entry(self, action: str, actor: str, details: Dict[str, Any]):
        """Add audit entry"""
        self.audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "details": details
        })
    
    def validate_chain(self) -> Dict[str, Any]:
        """Validate audit chain integrity"""
        if len(self.audit_entries) < 2:
            return {"valid": True, "message": "Insufficient entries"}
        
        issues = []
        prev_timestamp = None
        
        for i, entry in enumerate(self.audit_entries):
            current_timestamp = datetime.fromisoformat(entry["timestamp"])
            
            if prev_timestamp and current_timestamp < prev_timestamp:
                issues.append(f"Non-chronological entry at index {i}")
            
            prev_timestamp = current_timestamp
        
        return {
            "valid": len(issues) == 0,
            "total_entries": len(self.audit_entries),
            "issues": issues
        }
    
    def get_report(self) -> str:
        """Generate audit report"""
        validation = self.validate_chain()
        
        report = []
        report.append("=" * 60)
        report.append("AUDIT TRAIL REPORT")
        report.append("=" * 60)
        report.append(f"Total Entries: {validation['total_entries']}")
        report.append(f"Chain Valid: {validation['valid']}")
        
        if validation['issues']:
            report.append("\nIssues Found:")
            for issue in validation['issues']:
                report.append(f"  - {issue}")
        
        report.append("\nRecent Entries:")
        for entry in self.audit_entries[-5:]:
            report.append(f"  {entry['timestamp']}: {entry['action']} by {entry['actor']}")
        
        return "\\n".join(report)
'''
    (LEGAL_DIR / "audit.py").write_text(audit_content)
    print("  [OK] Created: legal/audit.py")
    
    # compliance.py
    compliance_content = '''"""
Compliance Checker
"""

from typing import Dict, Any, List, Tuple


class ComplianceChecker:
    """Check compliance with regulations"""
    
    def __init__(self):
        self.requirements = {
            "data_retention": {"required": True, "description": "Data retention policy"},
            "audit_trail": {"required": True, "description": "Complete audit trail"},
            "encryption": {"required": True, "description": "Data encryption at rest"},
            "access_control": {"required": True, "description": "Access control"},
            "evidence_integrity": {"required": True, "description": "Evidence integrity verification"}
        }
    
    def check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance for given context"""
        results = {}
        
        for req_name, req_info in self.requirements.items():
            is_met = context.get(req_name, False)
            results[req_name] = {
                "required": req_info["required"],
                "met": is_met,
                "description": req_info["description"]
            }
        
        overall = all(r["met"] for r in results.values())
        
        return {
            "compliant": overall,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_violations(self, context: Dict[str, Any]) -> List[str]:
        """Get list of compliance violations"""
        result = self.check(context)
        return [
            f"{req}: {info['description']}"
            for req, info in result["checks"].items()
            if not info["met"]
        ]
    
    def generate_certificate(self, context: Dict[str, Any]) -> str:
        """Generate compliance certificate"""
        result = self.check(context)
        
        if not result["compliant"]:
            return "Compliance check failed. Cannot generate certificate."
        
        return f"""
COMPLIANCE CERTIFICATE
======================
Status: COMPLIANT
Timestamp: {result['timestamp']}

All requirements satisfied:
{chr(10).join(f'  [OK] {req}: {info["description"]}' for req, info in result["checks"].items())}

This certificate confirms that the system meets all compliance requirements.
"""
'''
    (LEGAL_DIR / "compliance.py").write_text(compliance_content)
    print("  [OK] Created: legal/compliance.py")
    
    # report.py
    report_content = '''"""
Legal Report Generator
"""

from typing import Dict, Any, List
from datetime import datetime


class LegalReportGenerator:
    """Generate legal reports"""
    
    def __init__(self):
        self.reports: List[Dict[str, Any]] = []
    
    def generate_evidence_report(self, evidence_data: List[Dict[str, Any]]) -> str:
        """Generate evidence report for legal purposes"""
        report = []
        report.append("=" * 70)
        report.append("LEGAL EVIDENCE REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Evidence Items: {len(evidence_data)}")
        report.append("")
        
        for i, evidence in enumerate(evidence_data[:20], 1):  # Limit for readability
            report.append(f"Evidence #{i}")
            report.append(f"  ID: {evidence.get('id', 'N/A')}")
            report.append(f"  Hash: {evidence.get('hash', 'N/A')[:16]}...")
            report.append(f"  Created: {evidence.get('created_at', 'N/A')}")
            report.append(f"  Source: {evidence.get('source', 'N/A')}")
            
            if evidence.get('custody_chain'):
                report.append(f"  Custody Events: {len(evidence['custody_chain'])}")
            
            report.append("")
        
        report.append("=" * 70)
        report.append("This report is generated for legal review purposes.")
        
        return "\\n".join(report)
    
    def generate_audit_report(self, audit_data: List[Dict[str, Any]]) -> str:
        """Generate audit report"""
        report = []
        report.append("=" * 70)
        report.append("AUDIT REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Audit Entries: {len(audit_data)}")
        report.append("")
        
        # Group by action
        actions = {}
        for entry in audit_data:
            action = entry.get('action', 'unknown')
            actions[action] = actions.get(action, 0) + 1
        
        report.append("Activity Summary:")
        for action, count in actions.items():
            report.append(f"  {action}: {count}")
        
        report.append("")
        report.append("Recent Activities:")
        for entry in audit_data[-10:]:
            report.append(f"  {entry.get('timestamp', 'N/A')}: {entry.get('action', 'N/A')} by {entry.get('actor', 'N/A')}")
        
        return "\\n".join(report)
    
    def generate_compliance_report(self, compliance_result: Dict[str, Any]) -> str:
        """Generate compliance report"""
        report = []
        report.append("=" * 70)
        report.append("COMPLIANCE REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Compliant: {compliance_result.get('compliant', False)}")
        report.append("")
        
        report.append("Requirement Checks:")
        for req, info in compliance_result.get('checks', {}).items():
            status = "[OK]" if info.get('met') else "[ERR]"
            report.append(f"  {status} {req}: {info.get('description', 'N/A')}")
        
        return "\\n".join(report)
'''
    (LEGAL_DIR / "report.py").write_text(report_content)
    print("  [OK] Created: legal/report.py")
    
    return True

def create_explainability_modules():
    """Buat Explainability modules"""
    
    # __init__.py
    init_content = '''"""
NEMESIS Explainability Module - Model Interpretability
"""

from backend.intelligence.explainability.explainer import ModelExplainer
from backend.intelligence.explainability.features import FeatureImportance
from backend.intelligence.explainability.reasoning import ReasoningEngine

__all__ = [
    'ModelExplainer',
    'FeatureImportance',
    'ReasoningEngine'
]
'''
    (EXPLAIN_DIR / "__init__.py").write_text(init_content)
    print("  [OK] Created: explainability/__init__.py")
    
    # explainer.py
    explainer_content = '''"""
Model Explainer - Explain Model Predictions
"""

from typing import Dict, Any, List, Optional
import numpy as np


class ModelExplainer:
    """Explain model predictions"""
    
    def __init__(self):
        self.explanations: List[Dict[str, Any]] = []
    
    def explain_prediction(
        self,
        prediction_id: str,
        features: Dict[str, float],
        prediction: float,
        model_type: str = "unknown"
    ) -> Dict[str, Any]:
        """Generate explanation for prediction"""
        
        # Sort features by importance (absolute value)
        sorted_features = sorted(
            features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        top_features = sorted_features[:5]
        
        # Generate natural language explanation
        if prediction > 0.7:
            verdict = "high risk"
        elif prediction > 0.4:
            verdict = "medium risk"
        else:
            verdict = "low risk"
        
        reasons = [
            f"Feature '{name}' contributed {value:.3f}"
            for name, value in top_features
        ]
        
        explanation = {
            "prediction_id": prediction_id,
            "prediction": prediction,
            "verdict": verdict,
            "model_type": model_type,
            "top_features": [
                {"name": name, "value": value}
                for name, value in top_features
            ],
            "reasons": reasons,
            "confidence": min(prediction, 1 - prediction) * 2  # Heuristic confidence
        }
        
        self.explanations.append(explanation)
        return explanation
    
    def get_explanation(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Get stored explanation"""
        for exp in self.explanations:
            if exp["prediction_id"] == prediction_id:
                return exp
        return None
    
    def generate_report(self, prediction_id: str) -> str:
        """Generate human-readable explanation report"""
        exp = self.get_explanation(prediction_id)
        if not exp:
            return "Explanation not found"
        
        report = []
        report.append("=" * 60)
        report.append("PREDICTION EXPLANATION")
        report.append("=" * 60)
        report.append(f"Prediction ID: {exp['prediction_id']}")
        report.append(f"Verdict: {exp['verdict'].upper()}")
        report.append(f"Score: {exp['prediction']:.3f}")
        report.append(f"Confidence: {exp['confidence']:.3f}")
        report.append("")
        report.append("Top Contributing Features:")
        for feature in exp['top_features']:
            report.append(f"  - {feature['name']}: {feature['value']:.3f}")
        report.append("")
        report.append("Reasoning:")
        for reason in exp['reasons']:
            report.append(f"  • {reason}")
        
        return "\\n".join(report)
'''
    (EXPLAIN_DIR / "explainer.py").write_text(explainer_content)
    print("  [OK] Created: explainability/explainer.py")
    
    # features.py
    features_content = '''"""
Feature Importance - Feature Attribution
"""

from typing import Dict, List, Any, Optional
import numpy as np


class FeatureImportance:
    """Compute feature importance"""
    
    def __init__(self):
        self.feature_history: Dict[str, List[float]] = {}
    
    def add_importance(self, feature_name: str, importance_value: float):
        """Record feature importance"""
        if feature_name not in self.feature_history:
            self.feature_history[feature_name] = []
        self.feature_history[feature_name].append(importance_value)
    
    def get_average_importance(self, feature_name: str) -> float:
        """Get average importance for feature"""
        if feature_name in self.feature_history:
            return float(np.mean(self.feature_history[feature_name]))
        return 0.0
    
    def get_top_features(self, n: int = 10) -> List[tuple]:
        """Get top N features by average importance"""
        averages = [
            (name, self.get_average_importance(name))
            for name in self.feature_history
        ]
        averages.sort(key=lambda x: x[1], reverse=True)
        return averages[:n]
    
    def get_feature_ranking(self) -> Dict[str, int]:
        """Get ranking of features"""
        averages = [
            (name, self.get_average_importance(name))
            for name in self.feature_history
        ]
        averages.sort(key=lambda x: x[1], reverse=True)
        
        return {name: rank for rank, (name, _) in enumerate(averages, 1)}
    
    def get_stability_score(self, feature_name: str) -> float:
        """Get stability of feature importance over time"""
        if feature_name not in self.feature_history:
            return 0.0
        
        values = self.feature_history[feature_name]
        if len(values) < 2:
            return 1.0
        
        # Low variance = high stability
        variance = np.var(values)
        return 1.0 / (1.0 + variance)
'''
    (EXPLAIN_DIR / "features.py").write_text(features_content)
    print("  [OK] Created: explainability/features.py")
    
    # reasoning.py
    reasoning_content = '''"""
Reasoning Engine - Generate Human-Readable Reasoning
"""

from typing import Dict, Any, List


class ReasoningEngine:
    """Generate human-readable reasoning for decisions"""
    
    def __init__(self):
        self.reasoning_templates = {
            "anomaly": "Anomaly detected: {description}",
            "collusion": "Potential collusion detected between {entities}",
            "risk": "Risk score {score} indicates {level} risk",
            "compliance": "Compliance check {status}: {details}"
        }
    
    def generate_reasoning(
        self,
        decision_type: str,
        data: Dict[str, Any],
        confidence: float
    ) -> str:
        """Generate reasoning text"""
        template = self.reasoning_templates.get(
            decision_type,
            "Decision based on analysis of {data}"
        )
        
        try:
            reasoning = template.format(**data)
        except KeyError:
            reasoning = f"Decision type '{decision_type}' with data: {data}"
        
        if confidence < 0.5:
            reasoning += " (Low confidence)"
        
        return reasoning
    
    def generate_detailed_reasoning(
        self,
        decision_type: str,
        features: Dict[str, float],
        prediction: float,
        threshold: float
    ) -> List[str]:
        """Generate detailed step-by-step reasoning"""
        reasoning = []
        
        reasoning.append(f"Decision Type: {decision_type}")
        reasoning.append(f"Prediction Score: {prediction:.3f}")
        reasoning.append(f"Decision Threshold: {threshold:.3f}")
        reasoning.append("")
        
        if prediction >= threshold:
            reasoning.append("DECISION: Positive/Flagged")
            reasoning.append("Reason: Score exceeds threshold")
        else:
            reasoning.append("DECISION: Negative/Clear")
            reasoning.append("Reason: Score below threshold")
        
        reasoning.append("")
        reasoning.append("Contributing Factors:")
        
        # Sort features by absolute value
        sorted_features = sorted(
            features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        for name, value in sorted_features[:5]:
            if value > 0:
                reasoning.append(f"  + {name}: +{value:.3f} (increases risk)")
            elif value < 0:
                reasoning.append(f"  - {name}: {value:.3f} (decreases risk)")
        
        return reasoning
'''
    (EXPLAIN_DIR / "reasoning.py").write_text(reasoning_content)
    print("  [OK] Created: explainability/reasoning.py")
    
    return True

def create_intel_init():
    """Buat __init__.py untuk intelligence"""
    content = '''"""
NEMESIS Intelligence Layer - AI/ML Capabilities
"""

from backend.intelligence.ml import AnomalyDetector, RiskScorer, ConfidenceCalibrator
from backend.intelligence.legal import AuditTrailValidator, ComplianceChecker, LegalReportGenerator
from backend.intelligence.explainability import ModelExplainer, FeatureImportance, ReasoningEngine

__all__ = [
    'AnomalyDetector',
    'RiskScorer',
    'ConfidenceCalibrator',
    'AuditTrailValidator',
    'ComplianceChecker',
    'LegalReportGenerator',
    'ModelExplainer',
    'FeatureImportance',
    'ReasoningEngine'
]
'''
    (INTEL_DIR / "__init__.py").write_text(content)
    print("  [OK] Created: intelligence/__init__.py")
    
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 2: RESTRUCTURE INTELLIGENCE LAYER")
    print("="*60)
    
    success = True
    success &= create_intel_structure()
    success &= create_ml_modules()
    success &= create_legal_modules()
    success &= create_explainability_modules()
    success &= create_intel_init()
    
    print("\n" + "="*60)
    if success:
        print("[OK] INTELLIGENCE LAYER RESTRUCTURED")
        print(f"   ML: {ML_DIR}")
        print(f"   Legal: {LEGAL_DIR}")
        print(f"   Explainability: {EXPLAIN_DIR}")
    else:
        print("[ERR] INTELLIGENCE LAYER RESTRUCTURE FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())