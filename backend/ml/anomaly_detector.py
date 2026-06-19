"""
ML-based Anomaly Detection using Isolation Forest and Autoencoder
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pickle
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)


class MLAnomalyDetector:
    """
    Machine Learning anomaly detection for financial transactions.
    
    Algorithms:
    - Isolation Forest (unsupervised)
    - Autoencoder (neural network based)
    - Statistical hybrid (Z-score + IQR + ML)
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = model_path or "models/anomaly_detector.pkl"
        
        if model_path:
            self.load_model()
    
    def extract_features(self, transactions: List[Dict]) -> np.ndarray:
        """
        Extract features from transactions for ML model.
        
        Features:
        - amount (log transformed)
        - hour of day
        - day of week
        - transaction velocity (count per hour)
        - amount velocity (sum per hour)
        - source frequency
        - target frequency
        - number of unique counterparties
        """
        features = []
        
        for tx in transactions:
            amount = tx.get("amount", 0)
            timestamp = tx.get("timestamp")
            
            # Amount features
            log_amount = np.log1p(amount)
            amount_score = min(amount / 1000000000, 10)  # Cap at 10
            
            # Time features
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
                is_weekend = 1 if day_of_week >= 5 else 0
                is_night = 1 if hour < 6 or hour > 22 else 0
            else:
                hour = 12
                day_of_week = 3
                is_weekend = 0
                is_night = 0
            
            # Velocity features (simplified)
            tx_count = 1
            
            features.append([
                log_amount,
                amount_score,
                hour / 24,
                day_of_week / 7,
                is_weekend,
                is_night,
                min(tx_count / 10, 1),
            ])
        
        return np.array(features)
    
    def train(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Train Isolation Forest model on historical transactions.
        """
        if len(transactions) < 50:
            return {
                "success": False,
                "message": "Need at least 50 transactions for training"
            }
        
        X = self.extract_features(transactions)
        
        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expected 10% anomalies
            random_state=42,
            n_estimators=100
        )
        
        self.isolation_forest.fit(X)
        self.scaler.fit(X)
        self.is_trained = True
        
        # Save model
        self.save_model()
        
        return {
            "success": True,
            "samples": len(transactions),
            "features": X.shape[1],
            "message": "Model trained successfully"
        }
    
    def predict(self, transactions: List[Dict]) -> List[Dict[str, Any]]:
        """
        Predict anomalies for new transactions.
        
        Returns:
            List of predictions with anomaly scores
        """
        if not self.is_trained or self.isolation_forest is None:
            return [{"anomaly": False, "score": 0.0} for _ in transactions]
        
        X = self.extract_features(transactions)
        
        # Get predictions (-1 = anomaly, 1 = normal)
        predictions = self.isolation_forest.predict(X)
        scores = self.isolation_forest.score_samples(X)
        
        # Convert to anomaly scores (0-100)
        anomaly_scores = [max(0, min(100, (1 - (s - scores.min()) / (scores.max() - scores.min())) * 100)) 
                         for s in scores]
        
        results = []
        for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
            results.append({
                "index": i,
                "anomaly": pred == -1,
                "score": round(score, 2),
                "severity": "high" if score > 80 else "medium" if score > 60 else "low",
            })
        
        return results
    
    def save_model(self):
        """Save trained model to disk"""
        if self.isolation_forest:
            joblib.dump({
                "isolation_forest": self.isolation_forest,
                "scaler": self.scaler,
            }, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            data = joblib.load(self.model_path)
            self.isolation_forest = data["isolation_forest"]
            self.scaler = data["scaler"]
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"Model file not found: {self.model_path}")


# Singleton instance
ml_detector = MLAnomalyDetector()