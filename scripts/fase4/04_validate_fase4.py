#!/usr/bin/env python3
"""
NEMESIS FASE 4 - Validation Script
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate():
    print("\n" + "="*60)
    print("FASE 4: VALIDATION")
    print("="*60)
    
    errors = []
    
    # 1. Check ML modules
    print("\n[1/5] Checking ML modules...")
    try:
        from backend.intelligence.ml.drift_detection import DataDriftDetector, ConceptDriftDetector
        detector = DataDriftDetector()
        print("  [OK] Drift detection")
    except Exception as e:
        errors.append(f"Drift detection: {e}")
    
    try:
        from backend.intelligence.ml.ensemble import EnsembleModel, VotingEnsemble
        ensemble = EnsembleModel([])
        print("  [OK] Ensemble models")
    except Exception as e:
        errors.append(f"Ensemble: {e}")
    
    try:
        from backend.intelligence.ml.feature_store import FeatureStore
        store = FeatureStore()
        print("  [OK] Feature store")
    except Exception as e:
        errors.append(f"Feature store: {e}")
    
    # 2. Check Explainability modules
    print("\n[2/5] Checking Explainability modules...")
    try:
        from backend.intelligence.explainability.lime import LimeExplainer
        lime = LimeExplainer()
        print("  [OK] LIME explainer")
    except Exception as e:
        errors.append(f"LIME: {e}")
    
    try:
        from backend.intelligence.explainability.shap_adapter import ShapAdapter
        shap = ShapAdapter()
        print("  [OK] SHAP adapter")
    except Exception as e:
        print(f"  [WARN] SHAP adapter not available: {e}")
        # Don't count as error - SHAP is optional
    
    # 3. Check Pipeline modules
    print("\n[3/5] Checking Pipeline modules...")
    try:
        from backend.intelligence.pipeline import ModelTrainer, BatchPredictor, ModelValidator
        trainer = ModelTrainer()
        print("  [OK] Model trainer")
    except Exception as e:
        errors.append(f"Trainer: {e}")
    
    try:
        predictor = BatchPredictor(None)
        print("  [OK] Batch predictor")
    except Exception as e:
        errors.append(f"Predictor: {e}")
    
    try:
        validator = ModelValidator()
        print("  [OK] Model validator")
    except Exception as e:
        errors.append(f"Validator: {e}")
    
    # 4. Integration test
    print("\n[4/5] Integration test...")
    try:
        from backend.intelligence.ml.anomaly import AnomalyDetector
        from backend.intelligence.ml.scoring import RiskScorer
        from backend.intelligence.ml.ensemble import EnsembleModel
        
        detector = AnomalyDetector()
        scorer = RiskScorer()
        
        data = [1, 2, 3, 100, 4, 5, 6]
        anomalies = detector.detect(data)
        
        features = {"anomaly_score": 0.8, "collusion_risk": 0.6}
        score = scorer.compute_score(features)
        
        ensemble = EnsembleModel([
            {"model": scorer, "weight": 0.6, "name": "scorer"},
            {"model": detector, "weight": 0.4, "name": "detector"}
        ])
        
        ensemble_score = ensemble.predict(features)
        
        print(f"  [OK] Integration: anomalies={len(anomalies)}, score={score:.3f}, ensemble={ensemble_score:.3f}")
        
    except Exception as e:
        errors.append(f"Integration: {e}")
    
    # 5. Functional test
    print("\n[5/5] Functional test...")
    try:
        from backend.intelligence.ml.feature_store import FeatureStore
        from backend.intelligence.ml.drift_detection import DataDriftDetector
        
        store = FeatureStore()
        store.register_feature("test_feature", "numeric")
        store.set_feature("entity_1", "test_feature", 0.75)
        value = store.get_feature("entity_1", "test_feature")
        assert value == 0.75, "Feature store failed"
        print("  [OK] Feature store operations")
        
        drift = DataDriftDetector()
        drift.set_reference("test", [0.1, 0.2, 0.3, 0.4, 0.5])
        for i in range(100):
            drift.add_sample("test", 0.3 + np.random.normal(0, 0.1))
        result = drift.detect_drift("test")
        print(f"  [OK] Drift detection: {result['drift_detected']}")
        
    except Exception as e:
        errors.append(f"Functional: {e}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"[ERR] Validation failed: {len(errors)} errors")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[OK] All validations passed!")
        print("="*60)
        return True


import numpy as np

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
