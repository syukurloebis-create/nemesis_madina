"""
LIME Explainer - Local Interpretable Model-agnostic Explanations
"""

from typing import Dict, Any, List, Callable, Optional
import numpy as np
from copy import deepcopy


class LimeExplainer:
    """LIME-style local explanations"""
    
    def __init__(self, kernel_width: float = 0.25, n_samples: int = 5000):
        self.kernel_width = kernel_width
        self.n_samples = n_samples
    
    def explain_instance(
        self,
        instance: Dict[str, float],
        predict_fn: Callable,
        feature_names: List[str],
        num_features: int = 5
    ) -> Dict[str, Any]:
        """Generate local explanation for an instance"""
        instance_array = np.array([instance.get(f, 0.0) for f in feature_names])
        perturbed_samples = self._generate_perturbed_samples(instance_array, feature_names)
        
        predictions = []
        for sample in perturbed_samples:
            sample_dict = {f: sample[i] for i, f in enumerate(feature_names)}
            predictions.append(predict_fn(sample_dict))
        
        predictions = np.array(predictions)
        weights = self._calculate_weights(perturbed_samples, predictions, instance_array)
        
        top_indices = np.argsort(np.abs(weights))[-num_features:][::-1]
        
        explanations = []
        for idx in top_indices:
            explanations.append({
                "feature": feature_names[idx],
                "weight": float(weights[idx]),
                "value": instance.get(feature_names[idx], 0.0)
            })
        
        return {
            "explanations": explanations,
            "prediction": float(predictions[0]),
            "intercept": float(weights[-1]) if len(weights) > 0 else 0.0
        }
    
    def _generate_perturbed_samples(self, instance: np.ndarray, feature_names: List[str]) -> np.ndarray:
        """Generate perturbed samples around the instance"""
        n_features = len(feature_names)
        samples = np.zeros((self.n_samples, n_features))
        
        for i in range(self.n_samples):
            perturbation = np.random.normal(0, 0.1, n_features)
            samples[i] = instance + perturbation
            samples[i] = np.clip(samples[i], 0, 1)
        
        return samples
    
    def _calculate_weights(self, samples: np.ndarray, predictions: np.ndarray, instance: np.ndarray) -> np.ndarray:
        """Calculate feature weights using linear regression with kernel"""
        n_features = samples.shape[1]
        
        distances = np.linalg.norm(samples - instance, axis=1)
        weights = np.exp(-(distances ** 2) / (self.kernel_width ** 2))
        
        X = np.hstack([samples, np.ones((self.n_samples, 1))])
        W = np.diag(weights)
        
        try:
            beta = np.linalg.inv(X.T @ W @ X) @ (X.T @ W @ predictions)
            return beta[:-1]
        except np.linalg.LinAlgError:
            return np.zeros(n_features)
    
    def explain_prediction(self, instance: Dict[str, float], model: Any, feature_names: List[str], num_features: int = 5) -> Dict[str, Any]:
        """Convenience method to explain a model's prediction"""
        def predict_fn(features):
            if hasattr(model, 'predict'):
                return model.predict(features)
            elif hasattr(model, 'compute_score'):
                return model.compute_score(features)
            return 0.5
        return self.explain_instance(instance, predict_fn, feature_names, num_features)
    
    def generate_html_explanation(self, explanation: Dict[str, Any]) -> str:
        """Generate HTML visualization of explanation"""
        html_lines = []
        html_lines.append('<div class="lime-explanation">')
        html_lines.append(f'<h4>Prediction: {explanation["prediction"]:.3f}</h4>')
        html_lines.append('<table style="border-collapse: collapse; width: 100%;">')
        html_lines.append('<tr><th>Feature</th><th>Value</th><th>Weight</th><th>Contribution</th></tr>')
        
        for exp in explanation["explanations"]:
            contribution = exp["weight"] * exp["value"]
            color = "#4CAF50" if contribution > 0 else "#f44336"
            html_lines.append(f'<tr style="border-bottom: 1px solid #ddd;">')
            html_lines.append(f'<td>{exp["feature"]}</td>')
            html_lines.append(f'<td>{exp["value"]:.3f}</td>')
            html_lines.append(f'<td>{exp["weight"]:.3f}</td>')
            html_lines.append(f'<td style="color: {color}">{contribution:+.3f}</td>')
            html_lines.append('</tr>')
        
        html_lines.append('</table>')
        html_lines.append('</div>')
        
        return "\n".join(html_lines)
