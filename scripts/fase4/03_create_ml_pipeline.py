#!/usr/bin/env python3
"""
NEMESIS FASE 4 - ML Pipeline (Trainer, Predictor, Validator)
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PIPELINE_DIR = PROJECT_ROOT / "backend" / "intelligence" / "pipeline"

def create_pipeline_structure():
    """Create pipeline directory structure"""
    print("\n[1/4] Creating pipeline directory...")
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_content = '''"""
ML Pipeline - Training, Prediction, Validation Pipeline
"""

from backend.intelligence.pipeline.trainer import ModelTrainer
from backend.intelligence.pipeline.predictor import BatchPredictor
from backend.intelligence.pipeline.validator import ModelValidator

__all__ = ['ModelTrainer', 'BatchPredictor', 'ModelValidator']
'''
    (PIPELINE_DIR / "__init__.py").write_text(init_content)
    print("  [OK] Created __init__.py")
    return True

def create_trainer():
    """Create trainer.py for model training"""
    print("\n[2/4] Creating model trainer...")
    
    content = '''"""
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
'''
    
    file_path = PIPELINE_DIR / "trainer.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_predictor():
    """Create predictor.py for batch prediction"""
    print("\n[3/4] Creating batch predictor...")
    
    content = '''"""
Batch Predictor - Batch and Streaming Predictions
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from collections import deque
import asyncio


class BatchPredictor:
    """Handle batch and streaming predictions"""
    
    def __init__(self, model: Any):
        self.model = model
        self.prediction_history: List[Dict] = []
        self._stream_buffer: deque = deque(maxlen=1000)
    
    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[float]:
        """Make predictions for a batch of instances"""
        predictions = []
        
        for features in features_list:
            if hasattr(self.model, 'predict'):
                pred = self.model.predict(features)
            elif hasattr(self.model, 'compute_score'):
                pred = self.model.compute_score(features)
            else:
                pred = 0.5
            
            predictions.append(pred)
            
            # Record history
            self.prediction_history.append({
                "timestamp": datetime.now().isoformat(),
                "features": features,
                "prediction": pred
            })
        
        # Keep history manageable
        if len(self.prediction_history) > 10000:
            self.prediction_history = self.prediction_history[-5000:]
        
        return predictions
    
    def predict_stream(self, features: Dict[str, float]) -> float:
        """Make prediction for streaming data"""
        # Add to buffer
        self._stream_buffer.append(features)
        
        # Make prediction
        if hasattr(self.model, 'predict'):
            pred = self.model.predict(features)
        elif hasattr(self.model, 'compute_score'):
            pred = self.model.compute_score(features)
        else:
            pred = 0.5
        
        # Record
        self.prediction_history.append({
            "timestamp": datetime.now().isoformat(),
            "features": features,
            "prediction": pred,
            "stream": True
        })
        
        return pred
    
    async def predict_stream_async(self, features: Dict[str, float]) -> float:
        """Async prediction for streaming data"""
        # Simulate async processing
        await asyncio.sleep(0)
        return self.predict_stream(features)
    
    def predict_with_confidence(
        self,
        features: Dict[str, float],
        confidence_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Make prediction with confidence score"""
        prediction = self.predict_stream(features)
        
        if confidence_fn:
            confidence = confidence_fn(prediction)
        else:
            # Simple confidence based on distance from 0.5
            confidence = 1.0 - abs(prediction - 0.5) * 2
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_predictions(self, limit: int = 100) -> List[Dict]:
        """Get recent predictions"""
        return self.prediction_history[-limit:]
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        if not self.prediction_history:
            return {"error": "No predictions"}
        
        predictions = [p["prediction"] for p in self.prediction_history]
        
        return {
            "total_predictions": len(self.prediction_history),
            "mean": float(np.mean(predictions)),
            "std": float(np.std(predictions)),
            "min": float(min(predictions)),
            "max": float(max(predictions)),
            "high_risk_count": sum(1 for p in predictions if p > 0.7),
            "critical_risk_count": sum(1 for p in predictions if p > 0.9)
        }
    
    def clear_history(self):
        """Clear prediction history"""
        self.prediction_history = []
        self._stream_buffer.clear()


import numpy as np  # Add at top
'''
    
    file_path = PIPELINE_DIR / "predictor.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_validator():
    """Create validator.py for model validation"""
    print("\n[4/4] Creating model validator...")
    
    content = '''"""
Model Validator - Validate Model Performance
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class ModelValidator:
    """Validate model performance"""
    
    def __init__(self):
        self.validation_history: List[Dict] = []
    
    def validate_classification(
        self,
        predictions: List[float],
        actuals: List[float],
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Validate classification model"""
        if len(predictions) != len(actuals) or len(predictions) == 0:
            return {"error": "Invalid data"}
        
        # Convert to binary
        pred_binary = [1 if p > threshold else 0 for p in predictions]
        actual_binary = [1 if a > threshold else 0 for a in actuals]
        
        metrics = {
            "accuracy": float(accuracy_score(actual_binary, pred_binary)),
            "precision": float(precision_score(actual_binary, pred_binary, zero_division=0)),
            "recall": float(recall_score(actual_binary, pred_binary, zero_division=0)),
            "f1_score": float(f1_score(actual_binary, pred_binary, zero_division=0)),
        }
        
        # Calculate AUC if possible
        try:
            metrics["auc"] = float(roc_auc_score(actual_binary, predictions))
        except:
            metrics["auc"] = 0.5
        
        # Calculate calibration metrics
        metrics["brier_score"] = float(np.mean([(p - a) ** 2 for p, a in zip(predictions, actuals)]))
        
        # Log validation
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "samples": len(predictions),
            "type": "classification"
        })
        
        return metrics
    
    def validate_regression(
        self,
        predictions: List[float],
        actuals: List[float]
    ) -> Dict[str, Any]:
        """Validate regression model"""
        if len(predictions) != len(actuals) or len(predictions) == 0:
            return {"error": "Invalid data"}
        
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Calculate metrics
        mae = np.mean(np.abs(predictions - actuals))
        mse = np.mean((predictions - actuals) ** 2)
        rmse = np.sqrt(mse)
        
        # R-squared
        ss_res = np.sum((actuals - predictions) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        metrics = {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "r2": float(r2),
            "mean_prediction": float(np.mean(predictions)),
            "mean_actual": float(np.mean(actuals))
        }
        
        # Log validation
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "samples": len(predictions),
            "type": "regression"
        })
        
        return metrics
    
    def cross_validate(
        self,
        features: List[Dict[str, float]],
        labels: List[float],
        model_fn: callable,
        k_folds: int = 5
    ) -> Dict[str, Any]:
        """Perform k-fold cross-validation"""
        if len(features) < k_folds:
            return {"error": f"Insufficient data for {k_folds}-fold CV"}
        
        n_samples = len(features)
        fold_size = n_samples // k_folds
        
        fold_results = []
        
        for i in range(k_folds):
            # Split data
            val_start = i * fold_size
            val_end = (i + 1) * fold_size if i < k_folds - 1 else n_samples
            
            val_features = features[val_start:val_end]
            val_labels = labels[val_start:val_end]
            train_features = features[:val_start] + features[val_end:]
            train_labels = labels[:val_start] + labels[val_end:]
            
            # Train model (simplified)
            model = model_fn(train_features, train_labels)
            
            # Validate
            predictions = []
            for f in val_features:
                if hasattr(model, 'predict'):
                    pred = model.predict(f)
                else:
                    pred = 0.5
                predictions.append(pred)
            
            metrics = self.validate_regression(predictions, val_labels)
            fold_results.append(metrics)
        
        # Aggregate results
        avg_metrics = {}
        for key in fold_results[0].keys():
            if key != 'error':
                values = [r.get(key, 0) for r in fold_results]
                avg_metrics[key] = float(np.mean(values))
                avg_metrics[f"{key}_std"] = float(np.std(values))
        
        return {
            "mean_metrics": avg_metrics,
            "fold_results": fold_results,
            "k_folds": k_folds,
            "total_samples": n_samples
        }
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validations"""
        if not self.validation_history:
            return {"error": "No validations performed"}
        
        last_validation = self.validation_history[-1]
        
        return {
            "total_validations": len(self.validation_history),
            "last_validation": last_validation,
            "validation_types": {
                "classification": sum(1 for v in self.validation_history if v.get("type") == "classification"),
                "regression": sum(1 for v in self.validation_history if v.get("type") == "regression")
            }
        }
    
    def check_drift(self, current_metrics: Dict, reference_metrics: Dict, threshold: float = 0.1) -> Dict:
        """Check if model performance has drifted"""
        if not reference_metrics:
            return {"drift_detected": False, "reason": "No reference metrics"}
        
        drifted_metrics = []
        for key in current_metrics:
            if key in reference_metrics and key not in ['error']:
                current = current_metrics[key]
                reference = reference_metrics[key]
                relative_change = abs(current - reference) / (reference + 1e-10)
                
                if relative_change > threshold:
                    drifted_metrics.append({
                        "metric": key,
                        "current": current,
                        "reference": reference,
                        "change": relative_change
                    })
        
        return {
            "drift_detected": len(drifted_metrics) > 0,
            "drifted_metrics": drifted_metrics,
            "threshold": threshold
        }


from datetime import datetime  # Add at top
'''
    
    file_path = PIPELINE_DIR / "validator.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 4: ML PIPELINE")
    print("="*60)
    
    create_pipeline_structure()
    create_trainer()
    create_predictor()
    create_validator()
    
    print("\n" + "="*60)
    print("[OK] ML pipeline created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())