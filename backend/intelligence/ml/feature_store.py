"""
Feature Store - Centralized Feature Management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json


class FeatureStore:
    """Centralized store for features"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._features: Dict[str, Dict[str, Any]] = {}
        self._feature_history: Dict[str, List[tuple]] = defaultdict(list)
        self._feature_metadata: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
    
    def register_feature(self, name: str, feature_type: str, metadata: Dict[str, Any] = None):
        """Register a new feature"""
        self._feature_metadata[name] = {
            "name": name,
            "type": feature_type,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
    
    def set_feature(self, entity_id: str, feature_name: str, value: Any, timestamp: datetime = None):
        """Set feature value for an entity"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if entity_id not in self._features:
            self._features[entity_id] = {}
        
        self._features[entity_id][feature_name] = value
        self._feature_history[feature_name].append((timestamp, value, entity_id))
        
        # Keep history manageable
        if len(self._feature_history[feature_name]) > 10000:
            self._feature_history[feature_name] = self._feature_history[feature_name][-5000:]
    
    def get_feature(self, entity_id: str, feature_name: str) -> Optional[Any]:
        """Get feature value for an entity"""
        return self._features.get(entity_id, {}).get(feature_name)
    
    def get_features(self, entity_id: str) -> Dict[str, Any]:
        """Get all features for an entity"""
        return self._features.get(entity_id, {}).copy()
    
    def get_feature_history(self, feature_name: str, limit: int = 100) -> List[tuple]:
        """Get historical values for a feature"""
        return self._feature_history.get(feature_name, [])[-limit:]
    
    def get_feature_stats(self, feature_name: str) -> Dict[str, Any]:
        """Get statistics for a feature"""
        history = self.get_feature_history(feature_name, limit=1000)
        if not history:
            return {"error": "No data available"}
        
        values = [v for _, v, _ in history]
        
        return {
            "name": feature_name,
            "count": len(values),
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(min(values)),
            "max": float(max(values)),
            "recent": values[-10:]
        }
    
    def get_entity_vector(self, entity_id: str, feature_names: List[str] = None) -> Dict[str, float]:
        """Get feature vector for an entity"""
        features = self.get_features(entity_id)
        
        if feature_names:
            return {name: features.get(name, 0.0) for name in feature_names}
        return features
    
    def delete_entity_features(self, entity_id: str):
        """Delete all features for an entity"""
        if entity_id in self._features:
            del self._features[entity_id]
    
    def get_all_entities(self) -> List[str]:
        """Get all entity IDs with features"""
        return list(self._features.keys())
    
    def get_feature_metadata(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a feature"""
        return self._feature_metadata.get(feature_name)
    
    def list_features(self) -> List[str]:
        """List all registered features"""
        return list(self._feature_metadata.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall feature store statistics"""
        return {
            "total_entities": len(self._features),
            "total_features": len(self._feature_metadata),
            "features_with_history": len(self._feature_history),
            "total_feature_values": sum(len(v) for v in self._features.values())
        }


import numpy as np  # Add at top
