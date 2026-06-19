"""
Evidence Scoring Engine - Fixed JSONB
"""
import psycopg2
import json
from typing import Dict, Any
from datetime import datetime

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class EvidenceScoringEngine:
    WEIGHTS = {
        'source_reliability': 0.30,
        'hash_integrity': 0.25,
        'verification': 0.25,
        'correlation': 0.20
    }
    
    def calculate_trust_score(self, evidence_id: str) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    id,
                    case_id,
                    file_hash,
                    status,
                    verified_at,
                    file_type
                FROM evidence
                WHERE id = %s
            """, (evidence_id,))
            evidence = cur.fetchone()
            
            if not evidence:
                return {"error": "Evidence not found"}
            
            source_reliability = self._calculate_source_reliability(evidence[5])
            hash_integrity = self._calculate_hash_integrity(evidence[2])
            verification = self._calculate_verification_score(evidence[3], evidence[4])
            correlation = self._calculate_correlation_score(evidence_id)
            
            trust_score = (
                source_reliability * self.WEIGHTS['source_reliability'] +
                hash_integrity * self.WEIGHTS['hash_integrity'] +
                verification * self.WEIGHTS['verification'] +
                correlation * self.WEIGHTS['correlation']
            )
            trust_score = round(trust_score, 2)
            
            components = {
                'source_reliability': source_reliability,
                'hash_integrity': hash_integrity,
                'verification': verification,
                'correlation': correlation
            }
            
            result = {
                'evidence_id': evidence_id,
                'case_id': evidence[1],
                'trust_score': trust_score,
                'confidence_level': self._get_confidence_level(trust_score),
                'components': components,
                'calculated_at': datetime.now().isoformat()
            }
            
            # Save to database - convert dict to JSON string
            self._save_score(evidence_id, trust_score, json.dumps(components))
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()
    
    def _calculate_source_reliability(self, file_type: str) -> float:
        if not file_type:
            return 50.0
        ft = file_type.lower()
        if 'pdf' in ft:
            return 90.0
        elif 'excel' in ft or 'spreadsheet' in ft or 'xls' in ft:
            return 85.0
        elif 'image' in ft or 'png' in ft or 'jpg' in ft or 'jpeg' in ft:
            return 70.0
        elif 'audio' in ft or 'mp3' in ft or 'wav' in ft:
            return 65.0
        else:
            return 60.0
    
    def _calculate_hash_integrity(self, file_hash: str) -> float:
        return 100.0 if file_hash else 0.0
    
    def _calculate_verification_score(self, status: str, verified_at) -> float:
        if status == 'verified' and verified_at:
            return 100.0
        elif status == 'verified':
            return 80.0
        elif status == 'pending':
            return 60.0
        elif status == 'rejected':
            return 0.0
        return 50.0
    
    def _calculate_correlation_score(self, evidence_id: str) -> float:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*) 
                FROM evidence 
                WHERE case_id = (
                    SELECT case_id FROM evidence WHERE id = %s
                )
                AND id != %s
            """, (evidence_id, evidence_id))
            count = cur.fetchone()[0]
            if count >= 5:
                return 100.0
            elif count >= 3:
                return 80.0
            elif count >= 1:
                return 60.0
            else:
                return 30.0
        finally:
            cur.close()
            conn.close()
    
    def _get_confidence_level(self, score: float) -> str:
        if score >= 85:
            return 'HIGH'
        elif score >= 70:
            return 'MEDIUM'
        elif score >= 50:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _save_score(self, evidence_id: str, trust_score: float, components_json: str):
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE evidence 
                SET trust_score = %s, 
                    scoring_detail = %s::jsonb,
                    updated_at = NOW()
                WHERE id = %s
            """, (trust_score, components_json, evidence_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

scoring_engine = EvidenceScoringEngine()

def calculate_score(evidence_id: str) -> Dict[str, Any]:
    return scoring_engine.calculate_trust_score(evidence_id)
