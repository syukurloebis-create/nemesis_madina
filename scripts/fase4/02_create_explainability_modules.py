#!/usr/bin/env python3
"""
NEMESIS FASE 4 - Create Explainability Modules (LIME, SHAP)
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXPLAIN_DIR = PROJECT_ROOT / "backend" / "intelligence" / "explainability"

def create_lime_explainer():
    """Create lime.py for LIME explanations"""
    print("\n[1/3] Creating LIME explainer...")
    
    content = '''"""
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
        
        return "\\n".join(html_lines)
'''
    
    file_path = EXPLAIN_DIR / "lime.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_shap_adapter():
    """Create shap_adapter.py for SHAP explanations"""
    print("\n[2/3] Creating SHAP adapter...")
    
    content = '''"""
SHAP Adapter - SHAP (SHapley Additive exPlanations) Adapter
"""

from typing import Dict, Any, List, Callable, Optional
import numpy as np


class ShapAdapter:
    """SHAP-style explanations using kernel SHAP approximation"""
    
    def __init__(self, n_samples: int = 100):
        self.n_samples = n_samples
    
    def explain(self, instance: Dict[str, float], predict_fn: Callable, feature_names: List[str], background_data: Optional[List[Dict[str, float]]] = None) -> Dict[str, Any]:
        """Generate SHAP explanations for an instance"""
        n_features = len(feature_names)
        instance_array = np.array([instance.get(f, 0.0) for f in feature_names])
        
        if background_data is None:
            background_array = np.random.uniform(0, 1, (self.n_samples, n_features))
        else:
            background_array = np.array([[b.get(f, 0.0) for f in feature_names] for b in background_data[:self.n_samples]])
        
        shap_values = self._kernel_shap(instance_array, background_array, predict_fn, feature_names)
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
    
    def _kernel_shap(self, instance: np.ndarray, background: np.ndarray, predict_fn: Callable, feature_names: List[str]) -> np.ndarray:
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
            lines.append(f"  {exp['feature']}: {exp['shap_value']:+.3f} ({direction} risk, value={exp['value']:.3f})")
        
        return "\\n".join(lines)
    
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
            bar = "█" * bar_length if exp["shap_value"] > 0 else "░" * bar_length
            lines.append(f"{sign} {exp['feature']:20} {bar} {current:.3f}")
        
        lines.append("-" * 50)
        lines.append(f"Final prediction: {explanation['prediction']:.3f}")
        
        return "\\n".join(lines)
'''
    
    file_path = EXPLAIN_DIR / "shap_adapter.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def enhance_existing_explainers():
    """Enhance existing explainer, features, reasoning files"""
    print("\n[3/3] Enhancing existing explainability modules...")
    
    # Enhance explainer.py
    explainer_path = EXPLAIN_DIR / "explainer.py"
    if explainer_path.exists():
        with open(explainer_path, 'a') as f:
            f.write('''

    def explain_counterfactual(self, instance: Dict[str, float], target_prediction: float, predict_fn: Callable, feature_names: List[str], max_iterations: int = 100) -> Dict[str, Any]:
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
            new_val = current_instance.get(feature, 0)
            if abs(new_val - original) > 0.01:
                changes.append({"feature": feature, "original": original, "new": new_val, "change": new_val - original})
        
        return {"explanation": "Counterfactual found", "original_prediction": current_prediction, "target_prediction": target_prediction, "new_prediction": predict_fn(current_instance), "changes": changes, "modified_instance": current_instance}
''')
        print("  [OK] Enhanced explainer.py")
    
    return True

def main():
    print("\n" + "="*60)
    print("FASE 4: EXPLAINABILITY MODULES")
    print("="*60)
    
    create_lime_explainer()
    create_shap_adapter()
    enhance_existing_explainers()
    
    print("\n" + "="*60)
    print("[OK] Explainability modules created")
    print("="*60)
    return 0

if __name__ == "__main__":
    from typing import Callable
    sys.exit(main())
