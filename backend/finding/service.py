from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.finding.models import Finding
import uuid
import logging

logger = logging.getLogger(__name__)

class AnomalyScoringService:
    
    @staticmethod
    def calculate_anomaly_score(evidence_list: list) -> float:
        if not evidence_list:
            return 0.5
        return min(0.3 + (len(evidence_list) * 0.1), 1.0)
    
    @staticmethod
    def determine_severity(anomaly_score: float, financial_loss: float = None) -> str:
        if financial_loss and financial_loss > 1_000_000_000:
            return "critical"
        elif financial_loss and financial_loss > 100_000_000:
            return "high"
        elif anomaly_score >= 0.8:
            return "critical"
        elif anomaly_score >= 0.6:
            return "high"
        elif anomaly_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def determine_finding_type(description: str) -> str:
        text = description.lower()
        if any(keyword in text for keyword in ['korupsi', 'suap', 'gratifikasi']):
            return "corruption"
        elif any(keyword in text for keyword in ['fraud', 'penipuan', 'palsu']):
            return "fraud"
        elif any(keyword in text for keyword in ['kolusi', 'kartel', 'persekongkolan']):
            return "collusion"
        else:
            return "anomaly"


class FindingService:
    
    @staticmethod
    async def create_finding_from_evidence(
        session: AsyncSession,
        case_id: str,
        evidence_ids: list,
        title: str,
        description: str,
        financial_loss: float = None,
        created_by: str = None,
        institution_id: str = None  # ← TAMBAHKAN parameter dengan default
    ) -> Finding:
        
        anomaly_score = AnomalyScoringService.calculate_anomaly_score(evidence_ids)
        severity = AnomalyScoringService.determine_severity(anomaly_score, financial_loss)
        finding_type = AnomalyScoringService.determine_finding_type(description)
        
        finding = Finding(
            id=str(uuid.uuid4()),
            case_id=case_id,
            institution_id=institution_id,  # ← GUNAKAN parameter
            title=title,
            description=description,
            finding_type=finding_type,
            severity=severity,
            status="DRAFT",
            evidence_ids=evidence_ids,
            anomaly_score=anomaly_score,
            confidence=anomaly_score,
            risk_score=anomaly_score * 100,
            financial_loss=financial_loss,
            created_by=created_by,
            detection_method="automated_anomaly_scoring",
            anomaly_details={
                "scoring_factors": {
                    "evidence_count": len(evidence_ids),
                    "anomaly_score": anomaly_score,
                    "risk_score": anomaly_score * 100
                }
            }
        )
        
        session.add(finding)
        await session.flush()
        
        return finding
    
    @staticmethod
    async def get_findings_by_case(
        session: AsyncSession,
        case_id: str
    ) -> list:
        result = await session.execute(
            select(Finding).where(Finding.case_id == case_id)
        )
        return result.scalars().all()
