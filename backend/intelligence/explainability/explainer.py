"""
Model Explainer - Explain Model Predictions
"""

from typing import Dict, Any, List, Optional, Callable
import numpy as np


class ModelExplainer:
    """Explain model predictions with multiple methods"""
    
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
        sorted_features = sorted(
            features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        top_features = sorted_features[:5]
        
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
            "confidence": min(prediction, 1 - prediction) * 2
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
            report.append(f"  * {reason}")
        
        return "\n".join(report)
    
    def explain_counterfactual(
        self,
        instance: Dict[str, float],
        target_prediction: float,
        predict_fn: Callable,
        feature_names: List[str],
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """Generate counterfactual explanation"""
        current_prediction = predict_fn(instance)
        
        if abs(current_prediction - target_prediction) < 0.1:
            return {"explanation": "Already close to target", "changes": []}
        
        step_size = 0.01
        current_instance = instance.copy()
        
        for _ in range(max_iterations):
            pred = predict_fn(current_instance)
            if abs(pred - target_prediction) < 0.05:
                break
            
            for feature in feature_names:
                if feature in current_instance:
                    change = step_size * (target_prediction - pred)
                    current_instance[feature] += change
                    current_instance[feature] = max(0, min(1, current_instance[feature]))
        
        changes = []
        for feature in feature_names:
            original = instance.get(feature, 0)
            new = current_instance.get(feature, 0)
            if abs(new - original) > 0.01:
                changes.append({
                    "feature": feature,
                    "original": original,
                    "new": new,
                    "change": new - original
                })
        
        return {
            "explanation": "Counterfactual found",
            "original_prediction": current_prediction,
            "target_prediction": target_prediction,
            "new_prediction": predict_fn(current_instance),
            "changes": changes,
            "modified_instance": current_instance
        }
