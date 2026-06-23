from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import json
import asyncio
from datetime import datetime
from sqlalchemy import text
from database import engine

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Get latest data
            data = await get_live_data()
            await websocket.send_json(data)
            await asyncio.sleep(30)  # Update setiap 30 detik
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def get_live_data():
    """Get live data untuk WebSocket"""
    try:
        with engine.connect() as conn:
            # Total cases
            result = conn.execute(text("SELECT COUNT(*) FROM cases"))
            total_cases = result.scalar() or 0
            
            # High risk
            result = conn.execute(text("SELECT COUNT(*) FROM cases WHERE risk_score >= 80"))
            high_risk = result.scalar() or 0
            
            # Active investigations
            result = conn.execute(text("""
                SELECT COUNT(*) FROM cases 
                WHERE workflow_stage IN ('SCREENING', 'ASSESSMENT', 'INVESTIGATION')
                AND status = 'OPEN'
            """))
            active = result.scalar() or 0
            
            # Evidence count
            result = conn.execute(text("SELECT COUNT(*) FROM evidence"))
            total_evidence = result.scalar() or 0
            
            # Verified evidence
            result = conn.execute(text("SELECT COUNT(*) FROM evidence WHERE status = 'verified'"))
            verified_evidence = result.scalar() or 0
            
            # Latest cases
            result = conn.execute(text("""
                SELECT id, title, risk_score, created_at 
                FROM cases 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            latest_cases = result.fetchall()
            
            return {
                "total_cases": total_cases,
                "high_risk": high_risk,
                "active": active,
                "total_evidence": total_evidence,
                "verified_evidence": verified_evidence,
                "latest_cases": [
                    {
                        "id": row[0],
                        "title": row[1],
                        "risk_score": float(row[2]) if row[2] else 0,
                        "created_at": row[3].isoformat() if row[3] else None
                    }
                    for row in latest_cases
                ],
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {"error": str(e)}
