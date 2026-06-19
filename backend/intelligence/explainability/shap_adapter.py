"""
SHAP Adapter - SHAP (SHapley Additive exPlanations) Adapter
"""

from typing import Dict, Any, List, Callable, Optional
import numpy as np


class ShapAdapter:
    """SHAP-style explanations using kernel SHAP approximation"""
    
    def __init__(self, n_samples: int = 100):
        self.n_samples = n_samples
    
    def explain(
        self,
        instance: Dict[str, float],
        predict_fn: Callable,
        feature_names: List[str],
        background_data: Optional[List[Dict[str, float]]] = None
    ) -> Dict[str, Any]:
        """Generate SHAP explanations for an instance"""
        n_features = len(feature_names)
        instance_array = np.array([instance.get(f, 0.0) for f in feature_names])
        
        if background_data is None:
            background_array = np.random.uniform(0, 1, (self.n_samples, n_features))
        else:
            background_array = np.array([
                [b.get(f, 0.0) for f in feature_names]
                for b in background_data[:self.n_samples]
            ])
        
        shap_values = self._kernel_shap(
            instance_array, background_array, predict_fn, feature_names
        )
        prediction = predict_fn(instance)
        
        base_value = np.mean([
            predict_fn({f: bg[i] for i, f in enumerate(feature_names)})
            for bg in background_array[:100]
        ])
        
        explanations = []
        for i, feature in enumerate(feature_names):
            explanations.append({
                "feature": feature,
                "shap_value": float(shap_values[i]),
                "value": instance.get(feature, 0.0),
                "contribution": float(shap_values[i])
            })
        
        explanations.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        return {
            "explanations": explanations,
            "prediction": float(prediction),
            "base_value": float(base_value),
            "feature_names": feature_names
        }
    
    def _kernel_shap(
        self,
        instance: np.ndarray,
        background: np.ndarray,
        predict_fn: Callable,
        feature_names: List[str]
    ) -> np.ndarray:
        """Kernel SHAP approximation"""
        n_features = len(instance)
        n_samples = min(self.n_samples, background.shape[0])
        
        coalitions = np.random.choice([0, 1], size=(n_samples, n_features))
        samples = np.zeros((n_samples, n_features))
        
        for i in range(n_samples):
            for j in range(n_features):
                if coalitions[i, j] == 1:
                    samples[i, j] = instance[j]
                else:
                    bg_idx = np.random.randint(background.shape[0])
                    samples[i, j] = background[bg_idx, j]
        
        predictions = []
        for sample in samples:
            sample_dict = {f: sample[i] for i, f in enumerate(feature_names)}
            predictions.append(predict_fn(sample_dict))
        predictions = np.array(predictions)
        
        shap_values = np.zeros(n_features)
        for i in range(n_features):
            with_feature = [s for s, c in zip(samples, coalitions) if c[i] == 1]
            with_pred = [p for p, c in zip(predictions, coalitions) if c[i] == 1]
            without_feature = [s for s, c in zip(samples, coalitions) if c[i] == 0]
            without_pred = [p for p, c in zip(predictions, coalitions) if c[i] == 0]
            
            if with_pred and without_pred:
                shap_values[i] = np.mean(with_pred) - np.mean(without_pred)
        
        return shap_values
    
    def summarize_explanation(self, explanation: Dict[str, Any]) -> str:
        """Generate summary of SHAP explanation"""
        lines = []
        lines.append("=" * 60)
        lines.append("SHAP EXPLANATION SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Prediction: {explanation['prediction']:.3f}")
        lines.append(f"Base Value: {explanation['base_value']:.3f}")
        lines.append("")
        lines.append("Top Contributing Features:")
        
        for exp in explanation["explanations"][:5]:
            direction = "increases" if exp["shap_value"] > 0 else "decreases"
            lines.append(
                f"  {exp['feature']}: {exp['shap_value']:+.3f} "
                f"({direction} risk, value={exp['value']:.3f})"
            )
        
        return "\n".join(lines)
    
    def generate_waterfall_plot(self, explanation: Dict[str, Any]) -> str:
        """Generate ASCII waterfall plot for explanation"""
        lines = []
        lines.append("Waterfall Plot:")
        lines.append("-" * 50)
        
        base = explanation["base_value"]
        current = base
        
        lines.append(f"Base value: {base:.3f}")
        
        for exp in explanation["explanations"][:8]:
            sign = "+" if exp["shap_value"] > 0 else "-"
            current += exp["shap_value"]
            bar_length = int(abs(exp["shap_value"]) * 50)
            bar = "#" * bar_length if exp["shap_value"] > 0 else "." * bar_length
            lines.append(f"{sign} {exp['feature']:20} {bar} {current:.3f}")
        
        lines.append("-" * 50)
        lines.append(f"Final prediction: {explanation['prediction']:.3f}")
        
        return "\n".join(lines)
