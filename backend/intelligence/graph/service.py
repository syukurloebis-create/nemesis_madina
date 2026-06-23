"""
Graph Intelligence Service
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import hashlib
import logging

from intelligence.graph.models import CollusionDetection
from intelligence.graph.extractors.entity_extractor import EntityExtractor
from intelligence.graph.graph_store import graph_store
from cases.event_store import get_case_events
from cases.service import CaseService
from telemetry.metrics import collusion_detections_total

logger = logging.getLogger(__name__)


class GraphIntelligenceService:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.entity_extractor = EntityExtractor()
    
    async def extract_entities_from_case(self, case_id: str) -> List[Dict[str, Any]]:
        events = await get_case_events(self.session, case_id)
        all_entities = []
        seen = set()
        
        case_service = CaseService(self.session)
        case = await case_service.get_case(case_id)
        
        if case and case.case_metadata:
            metadata_entities = self.entity_extractor.extract_from_case_metadata(case.case_metadata)
            for entity in metadata_entities:
                key = f"{entity['type']}:{entity['name']}"
                if key not in seen:
                    seen.add(key)
                    all_entities.append(entity)
        
        return all_entities
    
    async def ensure_graph_data(self, case_id: str) -> bool:
        graph = graph_store.get_graph(case_id)
        if not graph.get("nodes"):
            await self.extract_entities_from_case(case_id)
            case_service = CaseService(self.session)
            case = await case_service.get_case(case_id)
            if case and case.case_metadata:
                transactions = case.case_metadata.get("transactions", [])
                if transactions:
                    graph_store.add_transactions(case_id, transactions)
            return True
        return False
    
    async def analyze_collusion(self, case_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        if force_refresh:
            await self.ensure_graph_data(case_id)
        
        graph = graph_store.get_graph(case_id)
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        if len(nodes) < 3 or len(edges) < 3:
            return {
                "case_id": case_id,
                "entities_found": len(nodes),
                "edges_found": len(edges),
                "collusion_risk": 0,
                "triangles_found": 0,
                "detected_patterns": [],
                "saved_detections": 0,
                "graph_engine_used": False,
            }
        
        adj = defaultdict(set)
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if src and tgt:
                adj[src].add(tgt)
        
        node_ids = set(n["id"] for n in nodes)
        node_names = {n["id"]: n["name"] for n in nodes}
        
        triangles = []
        for a in node_ids:
            for b in adj.get(a, set()):
                if b not in node_ids:
                    continue
                for c in adj.get(b, set()):
                    if c not in node_ids:
                        continue
                    if a in adj.get(c, set()):
                        entities = [node_names.get(a, a), node_names.get(b, b), node_names.get(c, c)]
                        triangles.append({
                            "type": "financial_triangle",
                            "entities": entities,
                            "cycle": f"{entities[0]} → {entities[1]} → {entities[2]} → {entities[0]}",
                            "confidence": 0.85,
                            "severity": 0.7,
                        })
                        break
                else:
                    continue
                break
        
        unique = []
        seen = set()
        for t in triangles:
            key = "|".join(sorted(t["entities"]))
            if key not in seen:
                seen.add(key)
                unique.append(t)
        
        risk = len(unique) * 25 + 50 if unique else 0
        
        saved = 0
        for t in unique:
            pk = hashlib.md5("|".join(sorted(t["entities"])).encode()).hexdigest()
            
            result = await self.session.execute(
                select(CollusionDetection).where(CollusionDetection.case_id == case_id)
            )
            exists = False
            for ex in result.scalars().all():
                if ex.pattern_key == pk:
                    exists = True
                    break
            
            if not exists:
                det = CollusionDetection(
                    id=str(uuid.uuid4()),
                    case_id=case_id,
                    pattern_type=t.get("type"),
                    description=t.get("cycle"),
                    entity_names=t.get("entities"),
                    confidence=t.get("confidence"),
                    severity=t.get("severity"),
                    pattern_key=pk,
                )
                self.session.add(det)
                saved += 1
                
                # Track metrics - collusion detection
                collusion_detections_total.labels(pattern_type="financial_triangle").inc()
        
        await self.session.flush()
        
        return {
            "case_id": case_id,
            "entities_found": len(nodes),
            "edges_found": len(edges),
            "collusion_risk": risk,
            "triangles_found": len(unique),
            "detected_patterns": unique,
            "saved_detections": saved,
            "graph_engine_used": True,
        }
    
    async def get_collusion_summary(self, case_id: str) -> Dict[str, Any]:
        result = await self.session.execute(
            select(CollusionDetection).where(CollusionDetection.case_id == case_id)
        )
        detections = result.scalars().all()
        
        if not detections:
            return {"case_id": case_id, "has_collusion": False, "collusion_risk": 0, "patterns": []}
        
        return {
            "case_id": case_id,
            "has_collusion": True,
            "collusion_risk": max(d.severity for d in detections) * 100,
            "patterns": [
                {
                    "id": d.id,
                    "type": d.pattern_type,
                    "description": d.description,
                    "entities": d.entity_names,
                    "confidence": d.confidence,
                    "severity": d.severity,
                    "detected_at": d.detected_at.isoformat(),
                }
                for d in detections
            ],
        }