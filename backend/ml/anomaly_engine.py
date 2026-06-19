# backend/ml/anomaly_engine.py
import asyncio
import sqlite3
import time
import os
from datetime import datetime

async def detect_anomalies():
    """Deteksi anomaly berdasarkan rule (placeholder)."""
    print("🔍 Running anomaly detection...")
    return []

async def start_anomaly_engine():
    """Background task untuk anomaly detection."""
    print("🔄 Anomaly engine started (placeholder)")
    while True:
        try:
            anomalies = await detect_anomalies()
            if anomalies:
                print(f"⚠️ Detected {len(anomalies)} anomalies")
        except Exception as e:
            print(f"❌ Anomaly engine error: {e}")
        await asyncio.sleep(300)  # Setiap 5 menit
