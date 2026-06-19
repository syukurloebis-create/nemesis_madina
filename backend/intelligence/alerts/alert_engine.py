# alerts/alert_engine.py - Auto Alert Engine
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertEngine:
    """Auto Alert Engine for fraud detection"""

    @staticmethod
    async def process_fraud_patterns(db: AsyncSession) -> Dict[str, Any]:
        """Process fraud patterns and create alerts"""
        try:
            # Get high confidence fraud patterns
            patterns = await AlertEngine._get_high_confidence_patterns(db)
            
            alerts_created = 0
            for pattern in patterns:
                if await AlertEngine._create_alert(db, pattern):
                    alerts_created += 1
            
            return {
                "patterns_processed": len(patterns),
                "alerts_created": alerts_created,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error processing fraud patterns: {str(e)}")
            return {"status": "error", "error": str(e)}

    @staticmethod
    async def _get_high_confidence_patterns(db: AsyncSession):
        query = """
            SELECT 
                id,
                name,
                severity,
                confidence,
                description
            FROM fraud_patterns
            WHERE confidence >= 85
            AND status = 'ACTIVE'
            ORDER BY confidence DESC
        """
        result = await db.execute(text(query))
        return result.fetchall()

    @staticmethod
    async def _create_alert(db: AsyncSession, pattern) -> bool:
        try:
            # Check if alert already exists
            check_query = """
                SELECT id FROM alerts 
                WHERE pattern_id = :pattern_id AND status = 'OPEN'
            """
            result = await db.execute(
                text(check_query),
                {"pattern_id": str(pattern[0])}
            )
            if result.fetchone():
                return False
            
            # Create alert
            insert_query = """
                INSERT INTO alerts (
                    id,
                    pattern_id,
                    severity,
                    title,
                    description,
                    status,
                    created_at
                )
                VALUES (
                    gen_random_uuid(),
                    :pattern_id,
                    :severity,
                    :title,
                    :description,
                    'OPEN',
                    NOW()
                )
            """
            await db.execute(
                text(insert_query),
                {
                    "pattern_id": str(pattern[0]),
                    "severity": pattern[2],
                    "title": f"Fraud Alert: {pattern[1]}",
                    "description": pattern[4]
                }
            )
            await db.commit()
            logger.info(f"Alert created for pattern: {pattern[1]}")
            return True
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return False
