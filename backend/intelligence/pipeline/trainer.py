"""
Model Trainer - Train ML Models
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path
import numpy as np


class ModelTrainer:
    """Train and manage ML models"""
    
    def __init__(self, model_dir: Path = None):
        self.model_dir = model_dir or Path("./models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.training_history: Dict[str, List[Dict]] = {}
    
    def train_anomaly_model(
        self,
        data: List[float],
        model_name: str = "anomaly_model",
        method: str = "zscore"
    ) -> Dict[str, Any]:
        """Train anomaly detection model"""
        if len(data) < 10:
            return {"error": "Insufficient data"}
        
        mean = np.mean(data)
        std = np.std(data)
        
        model = {
            "type": "anomaly",
            "method": method,
            "mean": float(mean),
            "std": float(std),
            "threshold": 3.0,
            "trained_at": datetime.now().isoformat(),
            "training_samples": len(data)
        }
        
        self.models[model_name] = model
        
        # Record history
        if model_name not in self.training_history:
            self.training_history[model_name] = []
        self.training_history[model_name].append({
            "timestamp": datetime.now().isoformat(),
            "mean": mean,
            "std": std,
            "samples": len(data)
        })
        
        return model
    
    def train_scoring_model(
        self,
        features: List[Dict[str, float]],
        labels: List[float],
        model_name: str = "scoring_model"
    ) -> Dict[str, Any]:
        """Train risk scoring model"""
        if len(features) < 10:
            return {"error": "Insufficient data"}
        
        # Simple linear regression weights
        n_features = len(features[0]) if features else 0
        feature_names = list(features[0].keys()) if features else []
        
        # Calculate average feature importance
        weights = {}
        for fname in feature_names:
            values = [f.get(fname, 0) for f in features]
            correlation = np.corrcoef(values, labels)[0, 1] if len(values) > 1 else 0
            weights[fname] = max(0, correlation)
        
        # Normalize weights
        total = sum(weights.values())
        if total > 0:
            weights = {k: v/total for k, v in weights.items()}
        
        model = {
            "type": "scoring",
            "weights": weights,
            "trained_at": datetime.now().isoformat(),
            "training_samples": len(features),
            "feature_names": feature_names
        }
        
        self.models[model_name] = model
        
        # Record history
        if model_name not in self.training_history:
            self.training_history[model_name] = []
        self.training_history[model_name].append({
            "timestamp": datetime.now().isoformat(),
            "weights": weights,
            "samples": len(features)
        })
        
        return model
    
    def train_ensemble_model(
        self,
        models: List[Dict[str, Any]],
        validation_data: Tuple[List[Dict], List[float]],
        model_name: str = "ensemble_model"
    ) -> Dict[str, Any]:
        """Train ensemble model with optimized weights"""
        features, labels = validation_data
        
        if len(features) < 10:
            return {"error": "Insufficient validation data"}
        
        # Optimize ensemble weights
        n_models = len(models)
        weights = np.ones(n_models) / n_models
        
        # Simple grid search for weights
        best_weights = weights.copy()
        best_score = 0
        
        for i in range(n_models):
            for w in [0.1, 0.3, 0.5, 0.7, 0.9]:
                test_weights = weights.copy()
                test_weights[i] = w
                test_weights /= test_weights.sum()
                
                # Evaluate
                score = self._evaluate_ensemble(models, test_weights, features, labels)
                if score > best_score:
                    best_score = score
                    best_weights = test_weights
        
        model = {
            "type": "ensemble",
            "models": models,
            "weights": best_weights.tolist(),
            "trained_at": datetime.now().isoformat(),
            "validation_score": best_score
        }
        
        self.models[model_name] = model
        return model
    
    def _evaluate_ensemble(
        self,
        models: List[Dict],
        weights: np.ndarray,
        features: List[Dict],
        labels: List[float]
    ) -> float:
        """Evaluate ensemble performance"""
        predictions = []
        
        for model_dict in models:
            model = model_dict.get("model")
            if model and hasattr(model, 'compute_score'):
                preds = [model.compute_score(f) for f in features]
                predictions.append(preds)
        
        if not predictions:
            return 0.0
        
        # Weighted average
        ensemble_preds = np.average(predictions, axis=0, weights=weights)
        
        # Simple accuracy (within 0.1)
        correct = sum(1 for p, l in zip(ensemble_preds, labels) if abs(p - l) < 0.1)
        return correct / len(labels)
    
    def save_model(self, model_name: str, file_path: Path = None) -> bool:
        """Save model to disk"""
        if model_name not in self.models:
            return False
        
        if file_path is None:
            file_path = self.model_dir / f"{model_name}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.models[model_name], f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, model_name: str, file_path: Path = None) -> Optional[Dict]:
        """Load model from disk"""
        if file_path is None:
            file_path = self.model_dir / f"{model_name}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                model = json.load(f)
            self.models[model_name] = model
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a model"""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        history = self.training_history.get(model_name, [])
        
        return {
            "name": model_name,
            "type": model.get("type"),
            "trained_at": model.get("trained_at"),
            "training_samples": model.get("training_samples"),
            "training_history": history[-5:] if history else []
        }
    
    def list_models(self) -> List[str]:
        """List all trained models"""
        return list(self.models.keys())
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        if model_name in self.models:
            del self.models[model_name]
            return True
        return False
