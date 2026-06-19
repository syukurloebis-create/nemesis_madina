"""
Real-time WebSocket Alerts for NEMESIS MADINA
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict, Any, Set
import asyncio
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.user_connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.discard(websocket)
        self.user_connections.pop(user_id, None)
        logger.info(f"User {user_id} disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast failed: {e}")
    
    async def send_alert(self, alert: dict, user_id: str = None):
        """Send alert to specific user or broadcast if no user specified"""
        alert["timestamp"] = datetime.now().isoformat()
        
        if user_id:
            await self.send_personal_message(alert, user_id)
        else:
            await self.broadcast(alert)


manager = ConnectionManager()


class AlertEngine:
    """Alert generation engine"""
    
    def __init__(self):
        self.alert_rules = []
        self.alert_history: List[Dict] = []
    
    def register_rule(self, rule: Dict):
        """Register a new alert rule"""
        self.alert_rules.append(rule)
    
    async def check_collusion_risk(self, case_id: str, risk_score: float) -> List[Dict]:
        """Check if collusion risk triggers alert"""
        alerts = []
        
        if risk_score >= 80:
            alerts.append({
                "type": "CRITICAL_COLLUSION_RISK",
                "case_id": case_id,
                "risk_score": risk_score,
                "message": f"Critical collusion risk detected: {risk_score}/100",
                "severity": "critical",
                "action_required": "Immediate investigation required",
            })
        elif risk_score >= 60:
            alerts.append({
                "type": "HIGH_COLLUSION_RISK",
                "case_id": case_id,
                "risk_score": risk_score,
                "message": f"High collusion risk detected: {risk_score}/100",
                "severity": "high",
                "action_required": "Priority review needed",
            })
        
        return alerts
    
    async def check_anomaly(self, case_id: str, anomaly_score: float) -> List[Dict]:
        """Check if anomaly score triggers alert"""
        alerts = []
        
        if anomaly_score >= 70:
            alerts.append({
                "type": "HIGH_ANOMALY_DETECTED",
                "case_id": case_id,
                "anomaly_score": anomaly_score,
                "message": f"Unusual pattern detected: {anomaly_score}/100",
                "severity": "high",
                "action_required": "Review transaction patterns",
            })
        
        return alerts
    
    async def check_new_collusion(self, case_id: str, pattern: Dict) -> List[Dict]:
        """Check if new collusion pattern triggers alert"""
        alerts = []
        
        alerts.append({
            "type": "COLLUSION_PATTERN_DETECTED",
            "case_id": case_id,
            "pattern": pattern,
            "message": f"New collusion pattern detected: {pattern.get('type', 'unknown')}",
            "severity": "medium",
            "action_required": "Verify pattern and update case",
        })
        
        return alerts
    
    async def process_and_send(
        self,
        case_id: str,
        alerts: List[Dict],
        user_id: str = None
    ):
        """Process alerts and send via WebSocket"""
        for alert in alerts:
            alert["alert_id"] = f"alert_{datetime.now().timestamp()}"
            alert["case_id"] = case_id
            self.alert_history.append(alert)
            
            await manager.send_alert(alert, user_id)
            logger.info(f"Alert sent: {alert['type']} for case {case_id}")


alert_engine = AlertEngine()


# WebSocket endpoint
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to alert system",
            "timestamp": datetime.now().isoformat(),
        }, user_id)
        
        while True:
            # Receive heartbeat
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)