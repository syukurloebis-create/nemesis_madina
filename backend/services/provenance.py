"""
Decision Provenance Engine - Fixed dengan JOIN
"""
import psycopg2
from typing import Dict, Any, List
from datetime import datetime

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class DecisionProvenanceEngine:

    def get_provenance(self, case_id: str) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # 1. Get case info
            cur.execute("""
                SELECT id, title, status, risk_score, risk_level, workflow_stage
                FROM cases WHERE id = %s
            """, (case_id,))
            case = cur.fetchone()
            
            if not case:
                return {"error": "Case not found"}
            
            # 2. Get evidence
            evidence = self._get_evidence(case_id, cur)
            
            # 3. Get risk factors
            risk_factors = self._get_risk_factors(case_id, cur)
            
            # 4. Get findings via case_id
            findings = self._get_findings(case_id, cur)
            
            # 5. Get recommendations via findings
            recommendations = self._get_recommendations(findings, cur)
            
            # 6. Get assertions
            assertions = self._get_assertions(case_id, cur)
            
            # 7. Build decision chain
            decision_chain = self._build_decision_chain(
                case, evidence, assertions, risk_factors, findings, recommendations
            )
            
            return {
                "case_id": case_id,
                "case_title": case[1],
                "status": case[2],
                "risk_score": case[3],
                "risk_level": case[4],
                "workflow_stage": case[5],
                "decision_chain": decision_chain,
                "summary": self._generate_summary(case, evidence, risk_factors, findings),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()
    
    def _get_evidence(self, case_id: str, cur) -> List[Dict]:
        cur.execute("""
            SELECT id, filename, status, trust_score, file_type, uploaded_at
            FROM evidence
            WHERE case_id = %s
            ORDER BY uploaded_at DESC
        """, (case_id,))
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "trust_score": float(row[3]) if row[3] else 0,
                "file_type": row[4],
                "uploaded_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    
    def _get_risk_factors(self, case_id: str, cur) -> List[Dict]:
        cur.execute("""
            SELECT factor, score, weight, contribution, description
            FROM risk_explanations
            WHERE case_id = %s
            ORDER BY contribution DESC
        """, (case_id,))
        rows = cur.fetchall()
        return [
            {
                "factor": row[0],
                "score": float(row[1]),
                "weight": float(row[2]),
                "contribution": float(row[3]),
                "description": row[4]
            }
            for row in rows
        ]
    
    def _get_findings(self, case_id: str, cur) -> List[Dict]:
        """Get findings langsung via case_id"""
        cur.execute("""
            SELECT id, finding_type, severity, description, status, created_at
            FROM investigation_findings
            WHERE case_id = %s
            ORDER BY created_at DESC
        """, (case_id,))
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "type": row[1],
                "severity": row[2],
                "description": row[3],
                "status": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    
    def _get_recommendations(self, findings: List[Dict], cur) -> List[Dict]:
        """Get recommendations via finding_id"""
        if not findings:
            return []
        
        finding_ids = [f['id'] for f in findings]
        placeholders = ','.join(['%s'] * len(finding_ids))
        
        cur.execute(f"""
            SELECT id, recommendation_type, description, priority, status, due_date, finding_id
            FROM investigation_recommendations
            WHERE finding_id IN ({placeholders})
            ORDER BY created_at DESC
        """, finding_ids)
        rows = cur.fetchall()
        
        # Map finding_id to finding_type
        finding_map = {f['id']: f['type'] for f in findings}
        
        return [
            {
                "id": row[0],
                "type": row[1],
                "description": row[2],
                "priority": row[3],
                "status": row[4],
                "due_date": row[5].isoformat() if row[5] else None,
                "finding_type": finding_map.get(row[6], "Unknown")
            }
            for row in rows
        ]
    
    def _get_assertions(self, case_id: str, cur) -> List[Dict]:
        assertions = []
        
        # High trust evidence
        cur.execute("""
            SELECT id, filename, trust_score
            FROM evidence
            WHERE case_id = %s AND trust_score >= 70
            ORDER BY trust_score DESC
            LIMIT 3
        """, (case_id,))
        top_evidence = cur.fetchall()
        
        for ev in top_evidence:
            assertions.append({
                "evidence_id": ev[0],
                "filename": ev[1],
                "statement": f"Evidence {ev[1][:30]}... memiliki tingkat kepercayaan tinggi ({float(ev[2])})",
                "confidence": float(ev[2])
            })
        
        # Risk factors
        cur.execute("""
            SELECT factor, description, contribution
            FROM risk_explanations
            WHERE case_id = %s AND contribution >= 20
            ORDER BY contribution DESC
            LIMIT 2
        """, (case_id,))
        top_risks = cur.fetchall()
        
        for risk in top_risks:
            assertions.append({
                "evidence_id": None,
                "filename": None,
                "statement": f"Faktor risiko: {risk[0]} - {risk[1][:50]}...",
                "confidence": float(risk[2])
            })
        
        return assertions
    
    def _build_decision_chain(self, case, evidence, assertions, risk_factors, findings, recommendations) -> List[Dict]:
        chain = []
        order = 1
        
        if evidence:
            chain.append({
                "order": order,
                "type": "evidence",
                "data": {
                    "total": len(evidence),
                    "verified": len([e for e in evidence if e['status'] == 'verified']),
                    "avg_trust": round(sum(e['trust_score'] for e in evidence) / len(evidence), 2) if evidence else 0
                }
            })
            order += 1
        
        if assertions:
            chain.append({
                "order": order,
                "type": "assertion",
                "data": assertions[:3]
            })
            order += 1
        
        if risk_factors:
            chain.append({
                "order": order,
                "type": "risk_factor",
                "data": risk_factors[:3]
            })
            order += 1
        
        if findings:
            chain.append({
                "order": order,
                "type": "finding",
                "data": findings[:2]
            })
            order += 1
        
        if recommendations:
            chain.append({
                "order": order,
                "type": "recommendation",
                "data": recommendations[:2]
            })
            order += 1
        
        if case:
            chain.append({
                "order": order,
                "type": "decision",
                "data": {
                    "status": case[2],
                    "risk_score": float(case[3]) if case[3] else 0,
                    "risk_level": case[4],
                    "workflow_stage": case[5]
                }
            })
        
        return chain
    
    def _generate_summary(self, case, evidence, risk_factors, findings) -> str:
        summary = f"Case: {case[1]}\n"
        summary += f"Risk Score: {case[3]} ({case[4]})\n"
        summary += f"Status: {case[2]}\n\n"
        
        if evidence:
            verified = len([e for e in evidence if e['status'] == 'verified'])
            summary += f"📄 Evidence: {len(evidence)} files ({verified} verified)\n"
        
        if risk_factors:
            top_risk = max(risk_factors, key=lambda x: x['contribution'])
            summary += f"⚠️ Top Risk: {top_risk['factor']} ({top_risk['contribution']}%)\n"
        
        if findings:
            summary += f"🔍 Findings: {len(findings)} identified\n"
        
        return summary

provenance_engine = DecisionProvenanceEngine()

def get_provenance(case_id: str) -> Dict[str, Any]:
    return provenance_engine.get_provenance(case_id)
