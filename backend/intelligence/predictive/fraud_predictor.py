"""
Fraud Prediction ML
Prediksi fraud dengan machine learning
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pickle
import json
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Hasil prediksi"""
    case_id: str
    probability: float
    risk_level: str
    confidence: float
    features: Dict[str, float]
    top_features: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "probability": self.probability,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "features": self.features,
            "top_features": self.top_features,
            "timestamp": self.timestamp.isoformat()
        }


class FraudPredictor:
    """
    Fraud Prediction Model
    Prediksi fraud menggunakan ensemble methods
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        self.metrics = {}
        self.threshold = 0.5

    def _init_features(self) -> List[str]:
        """Initialize feature names"""
        return [
            # Case features
            "case_risk_score",
            "case_age_days",
            "num_evidence",
            "avg_evidence_trust",

            # Vendor features
            "vendor_count",
            "vendor_concentration",
            "num_previous_cases",
            "avg_previous_risk",

            # Procurement features
            "contract_value",
            "price_deviation",
            "tender_count",
            "split_count",

            # Graph features
            "graph_degree",
            "collusion_score",
            "centrality_score",

            # Temporal features
            "activity_burst",
            "time_since_last",
            "transaction_frequency",

            # Fraud indicators
            "fraud_indicator_count",
            "anomaly_score",
            "red_flag_count"
        ]

    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from data"""
        features = []

        for feature_name in self.feature_names:
            value = data.get(feature_name, 0)
            # Normalize if needed
            if isinstance(value, (int, float)):
                features.append(float(value))
            else:
                features.append(0.0)

        return np.array(features).reshape(1, -1)

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Train the model
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train ensemble
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=random_state
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=random_state
            ),
            'logistic_regression': LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=random_state
            )
        }

        best_model = None
        best_score = 0

        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]

            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1': f1_score(y_test, y_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_test, y_prob)
            }

            logger.info(f"{name} metrics: {metrics}")

            # Use F1 score for model selection
            if metrics['f1'] > best_score:
                best_score = metrics['f1']
                best_model = model
                self.metrics = metrics

        self.model = best_model
        self.is_trained = True

        # Determine optimal threshold
        self.threshold = self._find_optimal_threshold(X_test_scaled, y_test)

        logger.info(f"Model trained successfully. Metrics: {self.metrics}")
        logger.info(f"Optimal threshold: {self.threshold:.3f}")

        return self.metrics

    def _find_optimal_threshold(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Find optimal threshold for classification"""
        if self.model is None:
            return 0.5

        y_prob = self.model.predict_proba(X_test)[:, 1]

        # Try different thresholds
        thresholds = np.arange(0.1, 0.9, 0.05)
        best_f1 = 0
        best_threshold = 0.5

        for threshold in thresholds:
            y_pred = (y_prob >= threshold).astype(int)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        return best_threshold

    def predict(self, case_id: str, data: Dict[str, Any]) -> PredictionResult:
        """
        Predict fraud probability for a case
        """
        if not self.is_trained or self.model is None:
            # Use rule-based fallback
            return self._fallback_prediction(case_id, data)

        # Prepare features
        features_array = self.prepare_features(data)
        features_scaled = self.scaler.transform(features_array)

        # Predict
        probability = self.model.predict_proba(features_scaled)[0, 1]
        confidence = self._calculate_confidence(probability)

        # Get feature importance
        feature_importance = self._get_feature_importance(data)

        # Determine risk level
        risk_level = self._get_risk_level(probability)

        return PredictionResult(
            case_id=case_id,
            probability=probability,
            risk_level=risk_level,
            confidence=confidence,
            features=data,
            top_features=feature_importance[:10]
        )

    def _fallback_prediction(self, case_id: str, data: Dict[str, Any]) -> PredictionResult:
        """Fallback rule-based prediction when model not trained"""
        # Calculate rule-based score
        score = 0
        factors = []

        # Check fraud indicators
        fraud_indicators = data.get("fraud_indicator_count", 0)
        if fraud_indicators > 3:
            score += 30
            factors.append({"name": "fraud_indicators", "value": fraud_indicators})

        # Check collusion
        collusion = data.get("collusion_score", 0)
        if collusion > 0.5:
            score += 25
            factors.append({"name": "collusion_score", "value": collusion})

        # Check price deviation
        deviation = data.get("price_deviation", 0)
        if deviation > 0.3:
            score += 20
            factors.append({"name": "price_deviation", "value": deviation})

        # Check case risk
        risk = data.get("case_risk_score", 0)
        if risk > 70:
            score += 15
            factors.append({"name": "case_risk_score", "value": risk})

        # Check vendor concentration
        concentration = data.get("vendor_concentration", 0)
        if concentration > 0.5:
            score += 10
            factors.append({"name": "vendor_concentration", "value": concentration})

        probability = min(score / 100, 1.0)
        risk_level = self._get_risk_level(probability)

        return PredictionResult(
            case_id=case_id,
            probability=probability,
            risk_level=risk_level,
            confidence=0.6,
            features=data,
            top_features=factors
        )

    def _calculate_confidence(self, probability: float) -> float:
        """Calculate confidence based on probability"""
        # Higher confidence when probability is far from 0.5
        distance = abs(probability - 0.5) * 2
        return min(0.5 + distance * 0.5, 0.95)

    def _get_risk_level(self, probability: float) -> str:
        """Get risk level based on probability"""
        if probability >= 0.7:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        return "LOW"

    def _get_feature_importance(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get feature importance"""
        if self.model and hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_names = self.feature_names

            # Get top features
            top_indices = np.argsort(importances)[::-1]
            return [
                {
                    "name": feature_names[i],
                    "importance": importances[i],
                    "value": data.get(feature_names[i], 0)
                }
                for i in top_indices[:10]
            ]

        # Fallback: use data values
        return [
            {"name": k, "importance": 0.5, "value": v}
            for k, v in data.items()
            if isinstance(v, (int, float))
        ][:10]

    def save_model(self, path: str) -> None:
        """Save model to file"""
        if not self.is_trained:
            raise ValueError("Model not trained")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'metrics': self.metrics,
            'threshold': self.threshold
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {path}")

    def load_model(self, path: str) -> None:
        """Load model from file"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        self.metrics = model_data['metrics']
        self.threshold = model_data.get('threshold', 0.5)

        logger.info(f"Model loaded from {path}")


# Singleton instance
fraud_predictor = FraudPredictor()