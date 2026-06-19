"""
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
