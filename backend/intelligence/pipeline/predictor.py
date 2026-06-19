"""
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
