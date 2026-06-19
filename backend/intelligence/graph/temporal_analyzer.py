"""
Temporal Analysis for Transaction Patterns
Detects velocity, bursts, and time-based anomalies
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import statistics


class TemporalAnalyzer:
    """
    Analyze temporal patterns in transactions and events.
    
    Features:
    - Transaction velocity (amount over time)
    - Burst detection (unusual concentration)
    - Time-based anomaly detection
    - Pattern periodicity
    """
    
    def __init__(self):
        self.velocity_threshold = 1_000_000_000  # 1M per day threshold
        self.burst_window_hours = 24
    
    def analyze_transaction_velocity(
        self,
        transactions: List[Dict],
        time_window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Analyze transaction velocity over time.
        
        Returns:
            - velocity_per_day: Amount per day
            - peak_day: Highest transaction day
            - average_velocity: Mean daily amount
            - risk_score: Velocity-based risk (0-100)
        """
        if not transactions:
            return {
                "velocity_per_day": {},
                "peak_day": None,
                "peak_amount": 0,
                "average_velocity": 0,
                "risk_score": 0,
                "is_anomalous": False,
            }
        
        # Group by day
        daily_amounts = defaultdict(float)
        timestamps = []
        
        for tx in transactions:
            timestamp = tx.get("timestamp")
            amount = tx.get("amount", 0)
            
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now(timezone.utc)
                
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                day_key = timestamp.strftime("%Y-%m-%d")
                daily_amounts[day_key] += amount
                timestamps.append(timestamp)
        
        if not daily_amounts:
            return {
                "velocity_per_day": {},
                "peak_day": None,
                "peak_amount": 0,
                "average_velocity": 0,
                "risk_score": 0,
                "is_anomalous": False,
            }
        
        # Calculate metrics
        amounts = list(daily_amounts.values())
        peak_day = max(daily_amounts, key=daily_amounts.get)
        peak_amount = daily_amounts[peak_day]
        average_velocity = statistics.mean(amounts) if amounts else 0
        
        # Detect velocity anomaly
        is_anomalous = peak_amount > self.velocity_threshold
        risk_score = min(100, (peak_amount / self.velocity_threshold) * 50) if peak_amount else 0
        
        return {
            "velocity_per_day": dict(daily_amounts),
            "peak_day": peak_day,
            "peak_amount": peak_amount,
            "average_velocity": round(average_velocity, 2),
            "risk_score": round(risk_score, 2),
            "is_anomalous": is_anomalous,
            "total_days": len(daily_amounts),
            "total_amount": sum(amounts),
        }
    
    def detect_burst_pattern(
        self,
        transactions: List[Dict],
        burst_threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Detect burst patterns (unusual concentration of transactions).
        
        Args:
            transactions: List of transactions
            burst_threshold: Number of transactions in window to consider burst
        
        Returns:
            - bursts: List of detected bursts
            - burst_risk: Risk score based on burst patterns
        """
        if len(transactions) < burst_threshold:
            return {"bursts": [], "burst_risk": 0, "has_burst": False}
        
        # Sort by timestamp
        sorted_txs = sorted(
            [tx for tx in transactions if tx.get("timestamp")],
            key=lambda x: x.get("timestamp", datetime.min)
        )
        
        bursts = []
        window_start = 0
        
        for i in range(len(sorted_txs)):
            window_txs = []
            window_end = i
            
            # Collect transactions within burst window
            for j in range(i, len(sorted_txs)):
                if j == i:
                    window_txs.append(sorted_txs[j])
                    continue
                
                time_diff = self._time_diff_hours(
                    sorted_txs[i].get("timestamp"),
                    sorted_txs[j].get("timestamp")
                )
                
                if time_diff <= self.burst_window_hours:
                    window_txs.append(sorted_txs[j])
                    window_end = j
                else:
                    break
            
            if len(window_txs) >= burst_threshold:
                total_amount = sum(tx.get("amount", 0) for tx in window_txs)
                bursts.append({
                    "start_time": sorted_txs[i].get("timestamp"),
                    "end_time": sorted_txs[window_end].get("timestamp"),
                    "transaction_count": len(window_txs),
                    "total_amount": total_amount,
                    "average_amount": total_amount / len(window_txs) if window_txs else 0,
                    "severity": min(1.0, len(window_txs) / 10),
                })
            
            i = window_end + 1
        
        # Calculate burst risk
        burst_risk = 0
        if bursts:
            max_severity = max(b.get("severity", 0) for b in bursts)
            burst_risk = min(100, max_severity * 100)
        
        return {
            "bursts": bursts,
            "burst_risk": round(burst_risk, 2),
            "has_burst": len(bursts) > 0,
            "total_bursts": len(bursts),
        }
    
    def detect_temporal_anomaly(
        self,
        transactions: List[Dict],
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect temporal anomalies in transaction patterns.
        
        Anomalies:
        - Unusual hour of day
        - Weekend vs weekday pattern
        - Sudden increase in frequency
        """
        if len(transactions) < 5:
            return {"anomalies": [], "anomaly_risk": 0}
        
        # Analyze hour distribution
        hour_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        
        for tx in transactions:
            timestamp = tx.get("timestamp")
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        continue
                
                hour_counts[timestamp.hour] += 1
                weekday_counts[timestamp.weekday()] += 1
        
        # Detect unusual hours (after 10 PM or before 6 AM)
        unusual_hours = []
        for hour, count in hour_counts.items():
            if hour >= 22 or hour <= 5:
                unusual_hours.append({"hour": hour, "count": count})
        
        # Detect weekend anomalies
        weekend_count = sum(weekday_counts.get(5, 0), weekday_counts.get(6, 0))
        weekday_count = sum(weekday_counts.get(i, 0) for i in range(5))
        weekend_ratio = weekend_count / (weekday_count + 1)
        
        anomalies = []
        anomaly_risk = 0
        
        if unusual_hours:
            anomalies.append({
                "type": "unusual_hours",
                "details": unusual_hours,
                "severity": min(0.7, len(unusual_hours) * 0.1),
            })
            anomaly_risk += 20
        
        if weekend_ratio > 0.5:
            anomalies.append({
                "type": "weekend_activity",
                "weekend_count": weekend_count,
                "weekday_count": weekday_count,
                "ratio": round(weekend_ratio, 2),
                "severity": min(0.8, weekend_ratio),
            })
            anomaly_risk += 30
        
        return {
            "anomalies": anomalies,
            "anomaly_risk": min(100, anomaly_risk),
            "has_anomaly": len(anomalies) > 0,
            "hour_distribution": dict(hour_counts),
            "weekday_distribution": dict(weekday_counts),
        }
    
    def _time_diff_hours(self, t1: Any, t2: Any) -> float:
        """Calculate time difference in hours between two timestamps."""
        if not t1 or not t2:
            return 999
        
        if isinstance(t1, str):
            try:
                t1 = datetime.fromisoformat(t1.replace('Z', '+00:00'))
            except:
                return 999
        
        if isinstance(t2, str):
            try:
                t2 = datetime.fromisoformat(t2.replace('Z', '+00:00'))
            except:
                return 999
        
        if t1.tzinfo is None:
            t1 = t1.replace(tzinfo=timezone.utc)
        if t2.tzinfo is None:
            t2 = t2.replace(tzinfo=timezone.utc)
        
        diff = abs((t2 - t1).total_seconds()) / 3600
        return diff
    
    def comprehensive_temporal_analysis(
        self,
        transactions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run all temporal analyses and return combined result.
        """
        velocity = self.analyze_transaction_velocity(transactions)
        burst = self.detect_burst_pattern(transactions)
        anomaly = self.detect_temporal_anomaly(transactions)
        
        # Calculate overall temporal risk
        temporal_risk = (
            velocity.get("risk_score", 0) * 0.4 +
            burst.get("burst_risk", 0) * 0.3 +
            anomaly.get("anomaly_risk", 0) * 0.3
        )
        
        return {
            "velocity_analysis": velocity,
            "burst_analysis": burst,
            "anomaly_analysis": anomaly,
            "temporal_risk": round(temporal_risk, 2),
            "transaction_count": len(transactions),
        }