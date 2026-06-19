"""
Ensemble Learning - Combine Multiple Models
"""

from typing import List, Dict, Any, Callable, Optional
from collections import defaultdict
import numpy as np


class EnsembleModel:
    """Ensemble of multiple models for improved accuracy"""
    
    def __init__(self, models: List[Dict[str, Any]]):
        """
        models: List of dicts with 'model', 'weight', 'name'
        """
        self.models = models
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normalize model weights to sum to 1"""
        total = sum(m.get('weight', 1.0) for m in self.models)
        if total > 0:
            for m in self.models:
                m['weight'] = m.get('weight', 1.0) / total
    
    def predict(self, features: Dict[str, float]) -> float:
        """Get weighted average prediction"""
        total_score = 0.0
        
        for model in self.models:
            model_instance = model['model']
            weight = model['weight']
            
            if hasattr(model_instance, 'predict'):
                score = model_instance.predict(features)
            elif hasattr(model_instance, 'compute_score'):
                score = model_instance.compute_score(features)
            else:
                score = 0.5
            
            total_score += score * weight
        
        return min(max(total_score, 0.0), 1.0)
    
    def predict_with_confidence(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Get prediction with confidence interval"""
        predictions = []
        weights = []
        
        for model in self.models:
            model_instance = model['model']
            weight = model['weight']
            
            if hasattr(model_instance, 'predict'):
                score = model_instance.predict(features)
            else:
                score = 0.5
            
            predictions.append(score)
            weights.append(weight)
        
        weighted_score = np.average(predictions, weights=weights)
        
        # Calculate confidence based on agreement
        variance = np.var(predictions)
        confidence = 1.0 - min(variance * 2, 1.0)
        
        return {
            "score": float(weighted_score),
            "confidence": float(confidence),
            "individual_scores": [
                {"model": m.get('name', f"model_{i}"), "score": s}
                for i, (m, s) in enumerate(zip(self.models, predictions))
            ]
        }
    
    def add_model(self, model: Any, weight: float = 1.0, name: str = None):
        """Add a new model to ensemble"""
        self.models.append({
            'model': model,
            'weight': weight,
            'name': name or f"model_{len(self.models)}"
        })
        self._normalize_weights()
    
    def remove_model(self, name: str):
        """Remove a model by name"""
        self.models = [m for m in self.models if m.get('name') != name]
        self._normalize_weights()
    
    def get_weights(self) -> Dict[str, float]:
        """Get current model weights"""
        return {m.get('name', f"model_{i}"): m['weight'] for i, m in enumerate(self.models)}
    
    def set_weights(self, weights: Dict[str, float]):
        """Set custom model weights"""
        for model in self.models:
            name = model.get('name')
            if name in weights:
                model['weight'] = weights[name]
        self._normalize_weights()


class VotingEnsemble:
    """Voting ensemble (majority vote) for classification"""
    
    def __init__(self, models: List[Any], voting: str = 'soft'):
        """
        voting: 'hard' for majority vote, 'soft' for probability average
        """
        self.models = models
        self.voting = voting
    
    def predict(self, features: Dict[str, float]) -> float:
        """Get ensemble prediction"""
        predictions = []
        
        for model in self.models:
            if hasattr(model, 'predict'):
                pred = model.predict(features)
            else:
                pred = 0.5
            predictions.append(pred)
        
        if self.voting == 'hard':
            # Convert to binary and take majority
            binary = [1 if p > 0.5 else 0 for p in predictions]
            majority = sum(binary) / len(binary)
            return majority
        else:
            # Soft voting - average probabilities
            return np.mean(predictions)
    
    def predict_with_agreement(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Get prediction with agreement level"""
        predictions = []
        
        for model in self.models:
            if hasattr(model, 'predict'):
                pred = model.predict(features)
            else:
                pred = 0.5
            predictions.append(pred)
        
        final_score = np.mean(predictions)
        
        # Agreement is 1 - variance
        agreement = 1.0 - min(np.var(predictions) * 2, 1.0)
        
        return {
            "score": float(final_score),
            "agreement": float(agreement),
            "predictions": predictions
        }
