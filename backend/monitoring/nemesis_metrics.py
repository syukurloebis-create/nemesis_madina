import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from monitoring.metrics import (
    nemesis_ingested_packages,
    nemesis_normalized_packages,
    nemesis_entity_nodes,
    nemesis_entity_edges,
    nemesis_risk_score,
    nemesis_anomaly_score,
    nemesis_anomaly_detected,
    nemesis_classification_count,
    nemesis_budget_total,
    nemesis_budget_trend,
    nemesis_hash_verification_failures,
    nemesis_evidence_hashes,
    nemesis_evidence_integrity_failures,
    nemesis_compliance_score,
    nemesis_ai_explanations,
    nemesis_red_flags,
    nemesis_benchmark_ratio,
    nemesis_deviation_index,
    nemesis_lineage_depth,
    nemesis_relationship_strength
)

logger = logging.getLogger(__name__)


class NemesisMetricsCollector:
    """Collector untuk metrics bisnis Nemesis V8+"""
    
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start metrics collection background task"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._collect_loop())
        logger.info("NemesisMetricsCollector started")
    
    async def stop(self):
        """Stop metrics collection"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("NemesisMetricsCollector stopped")
    
    async def _collect_loop(self):
        """Background loop untuk mengumpulkan metrics"""
        while self._running:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(60)  # Collect every 60 seconds
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(30)
    
    async def _collect_all_metrics(self):
        """Collect all business metrics from database"""
        await asyncio.gather(
            self._collect_package_metrics(),
            self._collect_risk_metrics(),
            self._collect_budget_metrics(),
            self._collect_audit_metrics(),
            self._collect_graph_metrics(),
            self._collect_ai_metrics(),
            self._collect_benchmark_metrics(),
            self._collect_compliance_metrics()
        )
    
    async def _collect_package_metrics(self):
        """Collect package-related metrics"""
        try:
            # Ingested packages
            nemesis_ingested_packages.labels(source='sirup').inc(0)
            nemesis_ingested_packages.labels(source='lkpp').inc(0)
            
            # Normalized packages
            nemesis_normalized_packages.labels(status='success').inc(0)
            nemesis_normalized_packages.labels(status='failed').inc(0)
            
            # Classifications
            classifications = ['LOW_RISK', 'MEDIUM_RISK', 'HIGH_RISK', 'ANOMALY', 'ABSURD']
            for cls in classifications:
                nemesis_classification_count.labels(classification=cls).set(0)
                
        except Exception as e:
            logger.error(f"Error collecting package metrics: {e}")
    
    async def _collect_risk_metrics(self):
        """Collect risk and anomaly metrics"""
        try:
            # This should query your database for actual risk scores
            # Example implementation:
            # async with get_db() as session:
            #     result = await session.execute(select(Package.risk_score))
            #     for row in result:
            #         nemesis_risk_score.labels(
            #             package_id=row.package_id,
            #             agency=row.agency,
            #             category=row.category
            #         ).set(row.risk_score)
            
            # For now, placeholder
            nemesis_anomaly_score.labels(package_id='sample').set(0)
            
        except Exception as e:
            logger.error(f"Error collecting risk metrics: {e}")
    
    async def _collect_budget_metrics(self):
        """Collect budget metrics"""
        try:
            # Budget by sector
            sectors = ['infrastructure', 'education', 'health', 'social']
            for sector in sectors:
                nemesis_budget_total.labels(sector=sector, year='2024').set(0)
            
            # Budget trend
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            for month in months:
                for sector in sectors:
                    nemesis_budget_trend.labels(sector=sector, month=month).set(0)
                    
        except Exception as e:
            logger.error(f"Error collecting budget metrics: {e}")
    
    async def _collect_audit_metrics(self):
        """Collect audit and integrity metrics"""
        try:
            # Evidence integrity
            nemesis_evidence_hashes.set(0)
            nemesis_evidence_integrity_failures.labels(evidence_id='sample').inc(0)
            
            # Hash chain failures
            nemesis_hash_verification_failures.labels(case_id='sample').inc(0)
            
        except Exception as e:
            logger.error(f"Error collecting audit metrics: {e}")
    
    async def _collect_graph_metrics(self):
        """Collect entity graph metrics"""
        try:
            # Nodes by type
            node_types = ['agency', 'vendor', 'package', 'category']
            for node_type in node_types:
                nemesis_entity_nodes.labels(node_type=node_type).set(0)
            
            # Edges by type
            edge_types = ['procures', 'wins', 'related', 'anomaly']
            for edge_type in edge_types:
                nemesis_entity_edges.labels(edge_type=edge_type).set(0)
            
            # Relationship strength
            nemesis_relationship_strength.labels(
                source='sample',
                target='sample',
                relationship_type='related'
            ).set(0)
            
        except Exception as e:
            logger.error(f"Error collecting graph metrics: {e}")
    
    async def _collect_ai_metrics(self):
        """Collect AI intelligence metrics"""
        try:
            # AI explanations
            reason_codes = ['price_unusual', 'pattern_repeated', 'vendor_monopoly']
            for code in reason_codes:
                nemesis_ai_explanations.labels(reason_code=code).inc(0)
            
            # Red flags by institution
            institutions = ['Inspektorat', 'BPKP', 'Kejaksaan', 'KPK']
            for inst in institutions:
                for severity in ['low', 'medium', 'high']:
                    nemesis_red_flags.labels(institution=inst, severity=severity).set(0)
                    
        except Exception as e:
            logger.error(f"Error collecting AI metrics: {e}")
    
    async def _collect_benchmark_metrics(self):
        """Collect benchmark metrics"""
        try:
            # Benchmark ratio
            nemesis_benchmark_ratio.labels(
                package_id='sample',
                sector='infrastructure'
            ).set(1.0)
            
            # Deviation index
            sectors = ['infrastructure', 'education', 'health']
            for sector in sectors:
                nemesis_deviation_index.labels(sector=sector, agency='sample').set(0)
            
            # Lineage depth
            nemesis_lineage_depth.labels(package_id='sample').set(0)
            
        except Exception as e:
            logger.error(f"Error collecting benchmark metrics: {e}")
    
    async def _collect_compliance_metrics(self):
        """Collect compliance metrics"""
        try:
            institutions = ['Inspektorat', 'BPKP', 'Kejaksaan', 'KPK']
            for inst in institutions:
                nemesis_compliance_score.labels(institution=inst).set(100)
        except Exception as e:
            logger.error(f"Error collecting compliance metrics: {e}")
    
    # ============================================
    # PUBLIC METHODS FOR UPDATING METRICS
    # ============================================
    
    def record_package_ingested(self, source: str):
        """Record when a package is ingested"""
        nemesis_ingested_packages.labels(source=source).inc()
    
    def record_package_normalized(self, status: str):
        """Record when a package is normalized"""
        nemesis_normalized_packages.labels(status=status).inc()
    
    def record_anomaly(self, severity: str, anomaly_type: str):
        """Record anomaly detection"""
        nemesis_anomaly_detected.labels(severity=severity, type=anomaly_type).inc()
    
    def record_hash_verification_failure(self, case_id: str):
        """Record hash chain verification failure"""
        nemesis_hash_verification_failures.labels(case_id=case_id).inc()
    
    def record_evidence_integrity_failure(self, evidence_id: str):
        """Record evidence integrity failure"""
        nemesis_evidence_integrity_failures.labels(evidence_id=evidence_id).inc()
    
    def update_risk_score(self, package_id: str, agency: str, category: str, score: float):
        """Update risk score for a package"""
        nemesis_risk_score.labels(
            package_id=package_id,
            agency=agency,
            category=category
        ).set(score)
    
    def update_anomaly_score(self, package_id: str, score: float):
        """Update anomaly score for a package"""
        nemesis_anomaly_score.labels(package_id=package_id).set(score)
    
    def update_compliance_score(self, institution: str, score: float):
        """Update compliance score for an institution"""
        nemesis_compliance_score.labels(institution=institution).set(score)
    
    def update_benchmark_ratio(self, package_id: str, sector: str, ratio: float):
        """Update benchmark ratio"""
        nemesis_benchmark_ratio.labels(package_id=package_id, sector=sector).set(ratio)
    
    def update_red_flag(self, institution: str, severity: str, count: int):
        """Update red flag count"""
        nemesis_red_flags.labels(institution=institution, severity=severity).set(count)


# Singleton instance
metrics_collector = NemesisMetricsCollector()