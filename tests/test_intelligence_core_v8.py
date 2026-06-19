"""
Unit Test untuk Intelligence Core V8+
Menjamin stabilisasi risk & trust score
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.intelligence.core.feature_engine import FeatureEngine
from backend.intelligence.core.risk_model import RiskModel
from backend.intelligence.core.trust_model import TrustModel
from backend.intelligence.core.calibration import Calibration


class TestFeatureEngine:
    """Test Feature Engine - Ekstraksi fitur dari events"""

    def test_empty_events(self):
        engine = FeatureEngine()
        features = engine.extract([])
        
        assert features["event_count"] == 0
        assert features["avg_pagu"] == 0
        assert features["pagu_coef_var"] == 0
        assert features["has_multiple_events"] == 0

    def test_single_event(self):
        engine = FeatureEngine()
        events = [{
            "payload": {"pagu": 1000000}
        }]
        features = engine.extract(events)
        
        assert features["event_count"] == 1
        assert features["avg_pagu"] == 1000000
        assert features["has_multiple_events"] == 0

    def test_multiple_events(self):
        engine = FeatureEngine()
        events = [
            {"payload": {"pagu": 1000000}},
            {"payload": {"pagu": 2000000}},
            {"payload": {"pagu": 1500000}}
        ]
        features = engine.extract(events)
        
        assert features["event_count"] == 3
        assert features["avg_pagu"] == 1500000
        assert features["has_multiple_events"] == 1
        assert features["pagu_std"] > 0

    def test_large_pagu_detection(self):
        engine = FeatureEngine()
        events = [{"payload": {"pagu": 2_000_000_000}}]  # 2 Milyar
        features = engine.extract(events)
        
        assert features["has_large_pagu"] == 1


class TestRiskModel:
    """Test Risk Model - Stabilized risk scoring"""

    def setup_method(self):
        self.risk_model = RiskModel()

    def test_no_data_case(self):
        """Entity tanpa data → risk moderate (0.30)"""
        features = {
            "event_count": 0,
            "avg_pagu": 0,
            "pagu_std": 0,
            "pagu_coef_var": 0,
            "has_multiple_events": 0,
            "has_large_pagu": 0
        }
        risk = self.risk_model.compute(features, anomaly_score=0)
        
        # Risk harus di range 0.25-0.35 untuk no data
        assert 0.25 <= risk <= 0.35, f"Risk {risk} di luar range"

    def test_small_pagu_low_risk(self):
        """Pagu kecil (Rp 10jt) → risk rendah"""
        features = {
            "event_count": 5,
            "avg_pagu": 10_000_000,
            "pagu_std": 1_000_000,
            "pagu_coef_var": 0.1,
            "has_multiple_events": 1,
            "has_large_pagu": 0
        }
        risk = self.risk_model.compute(features, anomaly_score=0)
        
        # Pagu kecil → risk < 0.4
        assert risk < 0.4, f"Risk {risk} terlalu tinggi untuk pagu kecil"

    def test_large_pagu_stable(self):
        """Pagu besar (Rp 1M) → risk stabil (0.45-0.65)"""
        features = {
            "event_count": 10,
            "avg_pagu": 1_000_000_000,
            "pagu_std": 50_000_000,
            "pagu_coef_var": 0.05,
            "has_multiple_events": 1,
            "has_large_pagu": 1
        }
        risk = self.risk_model.compute(features, anomaly_score=0)
        
        # Harus stabil, tidak panic ke 0.95
        assert 0.45 <= risk <= 0.65, f"Risk {risk} di luar range stabil"

    def test_anomaly_capped(self):
        """Anomaly tinggi (10) → tidak mendominasi"""
        features = {
            "event_count": 5,
            "avg_pagu": 100_000_000,
            "pagu_std": 10_000_000,
            "pagu_coef_var": 0.1,
            "has_multiple_events": 1,
            "has_large_pagu": 0
        }
        
        risk_without_anomaly = self.risk_model.compute(features, anomaly_score=0)
        risk_with_high_anomaly = self.risk_model.compute(features, anomaly_score=10)
        
        # Anomaly hanya meningkatkan risk sedikit (max +0.35)
        delta = risk_with_high_anomaly - risk_without_anomaly
        assert delta <= 0.35, f"Anomaly meningkatkan risk terlalu besar: {delta}"

    def test_volatility_increases_risk(self):
        """Volatility tinggi → risk lebih tinggi"""
        stable_features = {
            "event_count": 5,
            "avg_pagu": 100_000_000,
            "pagu_std": 1_000_000,
            "pagu_coef_var": 0.01,
            "has_multiple_events": 1,
            "has_large_pagu": 0
        }
        
        volatile_features = {
            "event_count": 5,
            "avg_pagu": 100_000_000,
            "pagu_std": 50_000_000,
            "pagu_coef_var": 0.5,
            "has_multiple_events": 1,
            "has_large_pagu": 0
        }
        
        stable_risk = self.risk_model.compute(stable_features, anomaly_score=0)
        volatile_risk = self.risk_model.compute(volatile_features, anomaly_score=0)
        
        assert volatile_risk > stable_risk, "Volatile harus punya risk lebih tinggi"


class TestTrustModel:
    """Test Trust Model - Trust aggregation"""

    def setup_method(self):
        self.trust_model = TrustModel()

    def test_low_risk_high_business(self):
        """Low risk + high business → HIGH trust"""
        result = self.trust_model.compute(risk_score=0.20, business_score=0.85)
        
        assert result["trust_level"] == "HIGH"
        assert result["trust_score"] > 0.75

    def test_high_risk_low_business(self):
        """High risk + low business → LOW trust"""
        result = self.trust_model.compute(risk_score=0.80, business_score=0.30)
        
        assert result["trust_level"] == "LOW"
        assert result["trust_score"] < 0.50

    def test_business_stabilization(self):
        """Business score ekstrem → di-stabilkan ke range 0.3-0.9"""
        # Business score 0 (error case)
        result_zero = self.trust_model.compute(risk_score=0.50, business_score=0)
        # Business score >1 (invalid)
        result_high = self.trust_model.compute(risk_score=0.50, business_score=5.0)
        
        # Kedua harus stabil di range reasonable
        assert 0.30 <= result_zero["components"]["stabilized_business"] <= 0.90
        assert 0.30 <= result_high["components"]["stabilized_business"] <= 0.90

    def test_trust_never_extreme(self):
        """Trust score tidak pernah 0 atau 1"""
        # Worst case
        worst = self.trust_model.compute(risk_score=1.0, business_score=0)
        # Best case
        best = self.trust_model.compute(risk_score=0, business_score=1.0)
        
        assert 0.1 <= worst["trust_score"] <= 0.95
        assert 0.1 <= best["trust_score"] <= 0.95


class TestCalibration:
    """Test Calibration - Stateful smoothing"""

    def setup_method(self):
        self.calibration = Calibration(max_history_minutes=60)

    def test_first_time_smoothing(self):
        """First time → return current value"""
        smoothed = self.calibration.smooth_risk("entity_1", 0.50)
        
        assert smoothed == 0.50

    def test_subsequent_smoothing(self):
        """Subsequent calls → smoothed"""
        self.calibration.smooth_risk("entity_1", 0.50)
        smoothed = self.calibration.smooth_risk("entity_1", 0.80)
        
        # Should be dampened: 0.70*0.50 + 0.30*0.80 = 0.35 + 0.24 = 0.59
        assert 0.58 <= smoothed <= 0.60

    def test_dampen_extreme(self):
        """Extreme scores (>0.85) → dampened"""
        # 0.95 → dampened
        dampened = self.calibration.dampen_extreme(0.95)
        assert dampened < 0.90
        
        # 0.80 → unchanged
        normal = self.calibration.dampen_extreme(0.80)
        assert normal == 0.80

    def test_clear_history(self):
        """Clear history resets smoothing"""
        self.calibration.smooth_risk("entity_1", 0.50)
        self.calibration.smooth_risk("entity_1", 0.80)
        
        # Clear
        self.calibration.clear_history("entity_1")
        
        # Now first time again
        reset = self.calibration.smooth_risk("entity_1", 0.90)
        assert reset == 0.90  # No smoothing


class TestIntegration:
    """End-to-end integration test"""

    def setup_method(self):
        self.feature_engine = FeatureEngine()
        self.risk_model = RiskModel()
        self.trust_model = TrustModel()
        self.calibration = Calibration()

    def test_full_pipeline_stable_entity(self):
        """Entity stabil dengan banyak events"""
        events = [
            {"payload": {"pagu": 100_000_000}} for _ in range(20)
        ]
        
        features = self.feature_engine.extract(events)
        raw_risk = self.risk_model.compute(features, anomaly_score=0)
        smoothed_risk = self.calibration.smooth_risk("stable_entity", raw_risk)
        trust = self.trust_model.compute(smoothed_risk, business_score=0.75)
        
        assert 0.25 <= smoothed_risk <= 0.45
        assert trust["trust_score"] > 0.65
        assert trust["trust_level"] in ["HIGH", "MEDIUM"]

    def test_full_pipeline_volatile_entity(self):
        """Entity dengan volatility tinggi"""
        events = [
            {"payload": {"pagu": 10_000_000}},
            {"payload": {"pagu": 1_000_000_000}},
            {"payload": {"pagu": 5_000_000}},
            {"payload": {"pagu": 2_000_000_000}},
        ]
        
        features = self.feature_engine.extract(events)
        raw_risk = self.risk_model.compute(features, anomaly_score=5)
        smoothed_risk = self.calibration.smooth_risk("volatile_entity", raw_risk)
        trust = self.trust_model.compute(smoothed_risk, business_score=0.50)
        
        # Volatile tapi tidak panic
        assert 0.40 <= smoothed_risk <= 0.70
        assert trust["trust_level"] in ["MEDIUM", "LOW"]

    def test_temporal_stability(self):
        """Multiple requests untuk entity yang sama harus stabil"""
        entity_id = "test_entity"
        
        scores = []
        for i in range(5):
            features = self.feature_engine.extract([
                {"payload": {"pagu": 100_000_000 + (i * 10_000_000)}}
            ])
            raw_risk = self.risk_model.compute(features, anomaly_score=2)
            smoothed = self.calibration.smooth_risk(entity_id, raw_risk)
            scores.append(smoothed)
        
        # Score tidak boleh liar
        max_variance = max(scores) - min(scores)
        assert max_variance < 0.20, f"Variance terlalu tinggi: {max_variance}"


class TestEdgeCases:
    """Edge cases & boundary testing"""

    def setup_method(self):
        self.risk_model = RiskModel()
        self.trust_model = TrustModel()

    def test_negative_pagu(self):
        """Negative pagu → handled gracefully"""
        features = {
            "event_count": 1,
            "avg_pagu": -1000000,
            "pagu_std": 0,
            "pagu_coef_var": 0,
            "has_multiple_events": 0,
            "has_large_pagu": 0
        }
        
        risk = self.risk_model.compute(features, anomaly_score=0)
        assert 0 <= risk <= 1, f"Risk {risk} di luar range"

    def test_missing_payload(self):
        """Event tanpa payload → tidak crash"""
        events = [{"something": "else"}]
        engine = FeatureEngine()
        
        features = engine.extract(events)
        assert features["avg_pagu"] == 0

    def test_string_pagu(self):
        """Pagu sebagai string → handled"""
        events = [{"payload": {"pagu": "1000000"}}]
        engine = FeatureEngine()
        
        # Should not crash
        features = engine.extract(events)
        # String '1000000' is not numeric, so should be 0
        assert features["avg_pagu"] == 0 or features["avg_pagu"] == 1000000


def print_test_summary(results):
    """Print test results summary"""
    print("\n" + "="*60)
    print("🧪 INTELLIGENCE CORE V8+ TEST RESULTS")
    print("="*60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    for r in results:
        status_icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"{status_icon} {r['name']}: {r['message']}")
    
    print("-"*60)
    print(f"Total: {passed} passed, {failed} failed")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
    print("="*60)


if __name__ == "__main__":
    # Run manual tests
    results = []
    
    # Test FeatureEngine
    test_fe = TestFeatureEngine()
    try:
        test_fe.test_empty_events()
        results.append({"name": "FeatureEngine - Empty Events", "status": "PASS", "message": "OK"})
    except Exception as e:
        results.append({"name": "FeatureEngine - Empty Events", "status": "FAIL", "message": str(e)})
    
    try:
        test_fe.test_large_pagu_detection()
        results.append({"name": "FeatureEngine - Large Pagu", "status": "PASS", "message": "OK"})
    except Exception as e:
        results.append({"name": "FeatureEngine - Large Pagu", "status": "FAIL", "message": str(e)})
    
    # Test RiskModel
    test_rm = TestRiskModel()
    test_rm.setup_method()
    
    try:
        test_rm.test_no_data_case()
        results.append({"name": "RiskModel - No Data", "status": "PASS", "message": "Risk dalam range"})
    except Exception as e:
        results.append({"name": "RiskModel - No Data", "status": "FAIL", "message": str(e)})
    
    try:
        test_rm.test_large_pagu_stable()
        results.append({"name": "RiskModel - Large Pagu Stable", "status": "PASS", "message": "Tidak panic"})
    except Exception as e:
        results.append({"name": "RiskModel - Large Pagu Stable", "status": "FAIL", "message": str(e)})
    
    try:
        test_rm.test_anomaly_capped()
        results.append({"name": "RiskModel - Anomaly Capped", "status": "PASS", "message": "Anomaly tidak dominan"})
    except Exception as e:
        results.append({"name": "RiskModel - Anomaly Capped", "status": "FAIL", "message": str(e)})
    
    # Test TrustModel
    test_tm = TestTrustModel()
    test_tm.setup_method()
    
    try:
        test_tm.test_trust_never_extreme()
        results.append({"name": "TrustModel - No Extreme", "status": "PASS", "message": "Trust 0.1-0.95"})
    except Exception as e:
        results.append({"name": "TrustModel - No Extreme", "status": "FAIL", "message": str(e)})
    
    try:
        test_tm.test_business_stabilization()
        results.append({"name": "TrustModel - Business Stabilizer", "status": "PASS", "message": "Business score stabilized"})
    except Exception as e:
        results.append({"name": "TrustModel - Business Stabilizer", "status": "FAIL", "message": str(e)})
    
    # Test Calibration
    test_cal = TestCalibration()
    test_cal.setup_method()
    
    try:
        test_cal.test_subsequent_smoothing()
        results.append({"name": "Calibration - Smoothing", "status": "PASS", "message": "Temporal smoothing works"})
    except Exception as e:
        results.append({"name": "Calibration - Smoothing", "status": "FAIL", "message": str(e)})
    
    try:
        test_cal.test_dampen_extreme()
        results.append({"name": "Calibration - Dampen Extreme", "status": "PASS", "message": "Extreme scores reduced"})
    except Exception as e:
        results.append({"name": "Calibration - Dampen Extreme", "status": "FAIL", "message": str(e)})
    
    # Test Integration
    test_int = TestIntegration()
    test_int.setup_method()
    
    try:
        test_int.test_temporal_stability()
        results.append({"name": "Integration - Temporal Stability", "status": "PASS", "message": "Score variance <0.20"})
    except Exception as e:
        results.append({"name": "Integration - Temporal Stability", "status": "FAIL", "message": str(e)})
    
    print_test_summary(results)