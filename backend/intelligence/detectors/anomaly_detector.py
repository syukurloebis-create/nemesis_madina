"""
Statistical Anomaly Detection Engine
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class AnomalyDetector:
    """
    Detects statistical anomalies in event data.
    
    Methods:
    - Z-score outlier detection
    - Interquartile range (IQR) detection
    - Temporal pattern anomaly
    - Frequency anomaly
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.threshold_zscore = self.config.get("threshold_zscore", 2.5)
        self.threshold_iqr = self.config.get("threshold_iqr", 1.5)
    
    def detect_amount_anomaly(
        self,
        amounts: List[float],
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous financial amounts using Z-score.
        
        Args:
            amounts: List of transaction/amount values
            metadata: Additional context (timestamps, categories)
            
        Returns:
            List of anomalies with indices and scores
        """
        if len(amounts) < 3:
            return []
        
        anomalies = []
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        if std == 0:
            return []
        
        for i, amount in enumerate(amounts):
            z_score = abs((amount - mean) / std)
            
            if z_score > self.threshold_zscore:
                anomalies.append({
                    "index": i,
                    "value": amount,
                    "z_score": round(z_score, 2),
                    "severity": min(z_score / 5, 1.0),
                    "type": "amount_anomaly",
                    "reason": f"Amount {amount} exceeds normal range (mean={mean:.2f}, std={std:.2f})"
                })
        
        return anomalies
    
    def detect_pattern_anomaly(
        self,
        values: List[Any],
        expected_patterns: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect unexpected patterns in sequential data.
        
        Examples:
        - Unusual status transition
        - Impossible timeline
        - Repeated suspicious action
        """
        anomalies = []
        
        # Detect repeated identical values (potential fraud pattern)
        from collections import Counter
        counter = Counter(values)
        
        for value, count in counter.items():
            if count > len(values) * 0.5 and len(values) > 3:
                anomalies.append({
                    "type": "repetition_anomaly",
                    "value": value,
                    "frequency": count,
                    "total": len(values),
                    "severity": min(count / len(values), 1.0),
                    "reason": f"Value '{value}' appears {count}/{len(values)} times (suspicious repetition)"
                })
        
        return anomalies
    
    def detect_temporal_anomaly(
        self,
        timestamps: List[datetime],
        expected_interval: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in time intervals between events.
        
        Args:
            timestamps: List of event timestamps
            expected_interval: Expected time between events in seconds
        """
        if len(timestamps) < 2:
            return []
        
        anomalies = []
        intervals = []
        
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        # Detect unusually short intervals (potential automation)
        for i, interval in enumerate(intervals):
            if interval < 0.1:  # Less than 100ms between events
                anomalies.append({
                    "index": i,
                    "interval_seconds": interval,
                    "type": "too_fast",
                    "severity": min(1.0, (0.1 - interval) / 0.1),
                    "reason": f"Events at {timestamps[i]} and {timestamps[i+1]} occurred {interval:.3f}s apart (suspiciously fast)"
                })
        
        # Detect unusually long intervals (potential investigation delay)
        if expected_interval:
            for i, interval in enumerate(intervals):
                if interval > expected_interval * 3:
                    anomalies.append({
                        "index": i,
                        "interval_seconds": interval,
                        "type": "too_slow",
                        "severity": min(1.0, interval / (expected_interval * 10)),
                        "reason": f"Unusual gap of {interval/3600:.1f} hours between events"
                    })
        
        return anomalies
    
    def detect_frequency_anomaly(
        self,
        events_by_day: Dict[str, int],
        baseline: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect unusual frequency of events.
        
        Args:
            events_by_day: Dict of date -> event count
            baseline: Expected frequency per day (default: mean)
        """
        if len(events_by_day) < 2:
            return []
        
        counts = list(events_by_day.values())
        mean = np.mean(counts)
        std = np.std(counts)
        
        anomalies = []
        
        for date, count in events_by_day.items():
            if std > 0:
                z_score = abs((count - mean) / std)
                if z_score > self.threshold_zscore:
                    anomalies.append({
                        "date": date,
                        "count": count,
                        "expected": round(mean, 1),
                        "z_score": round(z_score, 2),
                        "severity": min(z_score / 5, 1.0),
                        "type": "frequency_anomaly",
                        "reason": f"Unusual activity on {date}: {count} events (expected ~{mean:.1f})"
                    })
        
        return anomalies
    
    def detect_sequence_anomaly(
        self,
        sequence: List[str],
        invalid_transitions: Optional[List[Tuple[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect invalid state transitions.
        
        Args:
            sequence: List of states/events in order
            invalid_transitions: List of (from_state, to_state) that are not allowed
        """
        if not invalid_transitions:
            # Default: case status transitions
            valid_transitions = {
                "draft": ["open", "closed"],
                "open": ["investigating", "closed"],
                "investigating": ["verifying", "closed"],
                "verifying": ["resolved", "closed"],
                "resolved": ["closed"],
                "closed": []
            }
            invalid_transitions = []
            for from_state, to_states in valid_transitions.items():
                for to_state in to_states:
                    invalid_transitions.append((from_state, to_state))
        
        anomalies = []
        for i in range(1, len(sequence)):
            from_state = sequence[i-1]
            to_state = sequence[i]
            
            # Check if transition is allowed
            if (from_state, to_state) not in invalid_transitions:
                anomalies.append({
                    "index": i,
                    "from_state": from_state,
                    "to_state": to_state,
                    "type": "invalid_transition",
                    "severity": 0.8,
                    "reason": f"Invalid status transition: {from_state} → {to_state}"
                })
        
        return anomalies
    
    def analyze_case_events(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comprehensive anomaly analysis for a case's events.
        
        Args:
            events: List of event dictionaries with 'event_type', 'data', 'timestamp'
            
        Returns:
            Dict with all detected anomalies and overall risk score
        """
        if not events:
            return {"anomalies": [], "risk_score": 0.0, "summary": {}}
        
        all_anomalies = []
        
        # Extract data for analysis
        amounts = []
        event_types = []
        timestamps = []
        
        for event in events:
            event_type = event.get("event_type")
            data = event.get("data", {})
            timestamp = event.get("timestamp")
            
            event_types.append(event_type)
            
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        pass
                timestamps.append(timestamp)
            
            # Extract amounts from various event types
            if event_type == "transaction_added":
                amount = data.get("amount")
                if amount:
                    amounts.append(float(amount))
            elif event_type == "finding_created":
                score = data.get("anomaly_score")
                if score:
                    amounts.append(float(score))
        
        # Run detectors
        if amounts:
            amount_anomalies = self.detect_amount_anomaly(amounts)
            all_anomalies.extend(amount_anomalies)
        
        if len(event_types) > 2:
            pattern_anomalies = self.detect_pattern_anomaly(event_types)
            all_anomalies.extend(pattern_anomalies)
        
        if len(timestamps) > 1:
            temporal_anomalies = self.detect_temporal_anomaly(timestamps)
            all_anomalies.extend(temporal_anomalies)
        
        if len(events) > 1:
            sequence_anomalies = self.detect_sequence_anomaly(event_types)
            all_anomalies.extend(sequence_anomalies)
        
        # Calculate overall risk score
        if all_anomalies:
            risk_score = sum(a.get("severity", 0) for a in all_anomalies) / len(all_anomalies)
            risk_score = min(risk_score * 100, 100)  # Convert to 0-100
        else:
            risk_score = 0.0
        
        # Summarize by type
        summary = defaultdict(int)
        for anomaly in all_anomalies:
            summary[anomaly.get("type", "unknown")] += 1
        
        return {
            "anomalies": all_anomalies,
            "risk_score": round(risk_score, 2),
            "summary": dict(summary),
            "total_events": len(events),
            "anomaly_count": len(all_anomalies),
        }