"""
Anomaly Detection - Advanced Anomaly Detection
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy import stats
from collections import deque


class AnomalyDetector:
    """Advanced anomaly detection with multiple methods"""
    
    def __init__(self, threshold: float = 3.0, method: str = 'zscore'):
        self.threshold = threshold
        self.method = method  # zscore, iqr, isolation, mad
        self._history: deque = deque(maxlen=10000)
    
    def detect(self, data: List[float]) -> List[int]:
        """Detect anomalies in time series"""
        if len(data) < 10:
            return []
        
        if self.method == 'zscore':
            return self._detect_zscore(data)
        elif self.method == 'iqr':
            return self._detect_iqr(data)
        elif self.method == 'mad':
            return self._detect_mad(data)
        else:
            return self._detect_zscore(data)
    
    def _detect_zscore(self, data: List[float]) -> List[int]:
        """Z-score based anomaly detection"""
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs(value - mean) / std
            if z_score > self.threshold:
                anomalies.append(i)
        
        return anomalies
    
    def _detect_iqr(self, data: List[float]) -> List[int]:
        """IQR (Interquartile Range) based detection"""
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [i for i, v in enumerate(data) if v < lower_bound or v > upper_bound]
    
    def _detect_mad(self, data: List[float]) -> List[int]:
        """Median Absolute Deviation based detection"""
        median = np.median(data)
        mad = np.median([abs(x - median) for x in data])
        
        if mad == 0:
            return []
        
        modified_z_scores = [0.6745 * abs(x - median) / mad for x in data]
        
        return [i for i, z in enumerate(modified_z_scores) if z > self.threshold]
    
    def detect_online(self, value: float) -> Tuple[bool, float]:
        """Online anomaly detection (streaming)"""
        self._history.append(value)
        
        if len(self._history) < 50:
            return False, 0.0
        
        data = list(self._history)
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return False, 0.0
        
        z_score = abs(value - mean) / std
        is_anomaly = z_score > self.threshold
        
        return is_anomaly, float(z_score / self.threshold)
    
    def get_anomaly_score(self, value: float, historical: List[float]) -> float:
        """Get normalized anomaly score"""
        if not historical:
            return 0.0
        
        mean = np.mean(historical)
        std = np.std(historical)
        
        if std == 0:
            return 0.0
        
        z_score = abs(value - mean) / std
        return min(z_score / 5, 1.0)
    
    def get_seasonality_score(self, data: List[float], period: int = 24) -> float:
        """Detect seasonality strength"""
        if len(data) < period * 2:
            return 0.0
        
        # Split into periods
        periods = [data[i:i+period] for i in range(0, len(data) - period, period)]
        
        if len(periods) < 2:
            return 0.0
        
        # Calculate variance within periods and between periods
        within_var = np.mean([np.var(p) for p in periods])
        between_var = np.var([np.mean(p) for p in periods])
        
        if within_var == 0:
            return 1.0 if between_var > 0 else 0.0
        
        seasonality = between_var / (between_var + within_var)
        return float(seasonality)
    
    def update_threshold(self, new_threshold: float):
        """Update detection threshold"""
        self.threshold = new_threshold
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            "method": self.method,
            "threshold": self.threshold,
            "history_size": len(self._history)
        }
