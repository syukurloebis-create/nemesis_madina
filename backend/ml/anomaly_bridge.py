# backend/ml/anomaly_bridge.py
async def check_risk_anomaly(entity_id: str, risk_score: float):
    if risk_score > 0.8:
        # Insert anomaly ke SQLite
        cursor.execute("""
            INSERT INTO anomalies (entity_id, anomaly_type, severity, details, confidence, detected_at)
            VALUES (?, 'high_risk', 0.9, ?, ?, ?)
        """, entity_id, f"Risk score {risk_score} exceeds threshold", risk_score, time.time())
        
        # Broadcast via WebSocket
        await manager.broadcast({
            "type": "ANOMALY_DETECTED",
            "payload": {
                "entity_id": entity_id,
                "severity": "high",
                "risk_score": risk_score,
                "description": f"Critical risk detected: {risk_score*100}%"
            }
        })