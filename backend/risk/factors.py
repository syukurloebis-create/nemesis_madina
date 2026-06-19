# backend/risk/factors.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import math

from .framework import RiskFactor, RiskAssessmentRule, RiskCategory, get_risk_framework


class VendorRiskFactors:
    """Risk factors khusus untuk vendor"""
    
    @staticmethod
    def calculate_vendor_dominance(
        package_count: int,
        total_packages: int,
        total_value: float,
        total_value_all: float
    ) -> float:
        """Calculate vendor dominance score"""
        if total_packages == 0:
            return 0
        
        # Package share
        package_share = package_count / total_packages
        
        # Value share
        value_share = total_value / total_value_all if total_value_all > 0 else 0
        
        # Combined score (60% package share, 40% value share)
        dominance_score = (package_share * 0.6 + value_share * 0.4) * 100
        
        return min(100, dominance_score)
    
    @staticmethod
    def calculate_bid_rotation(
        bid_history: List[Dict[str, Any]],
        vendors: List[str],
        packages: List[str]
    ) -> float:
        """Calculate bid rotation suspicion score"""
        if len(bid_history) < 3:
            return 0
        
        # Detect rotation patterns
        rotation_count = 0
        for i in range(1, len(bid_history)):
            if i < len(vendors) - 1:
                if vendors[i] == vendors[i-1]:
                    rotation_count += 1
        
        rotation_rate = rotation_count / (len(bid_history) - 1)
        
        # Higher rotation rate = higher suspicion
        return min(100, rotation_rate * 100)
    
    @staticmethod
    def calculate_single_bidder_rate(
        single_bidder_packages: int,
        total_packages: int
    ) -> float:
        """Calculate single bidder rate"""
        if total_packages == 0:
            return 0
        
        rate = single_bidder_packages / total_packages
        return min(100, rate * 100)
    
    @staticmethod
    def calculate_price_markup(
        contract_price: float,
        market_price: float,
        reference_price: float
    ) -> float:
        """Calculate price markup suspicion score"""
        if market_price <= 0 and reference_price <= 0:
            return 0
        
        benchmark = max(market_price, reference_price)
        if benchmark <= 0:
            return 50
        
        markup_percentage = (contract_price - benchmark) / benchmark
        
        if markup_percentage <= 0:
            return 0
        elif markup_percentage <= 0.1:
            return 20
        elif markup_percentage <= 0.2:
            return 50
        elif markup_percentage <= 0.3:
            return 75
        else:
            return 100


class EntityRiskFactors:
    """Risk factors khusus untuk entity"""
    
    @staticmethod
    def calculate_conflict_of_interest(
        relationships: List[Dict[str, Any]],
        official_entities: List[str],
        vendor_entities: List[str]
    ) -> float:
        """Calculate conflict of interest score"""
        direct_connections = 0
        indirect_connections = 0
        
        for rel in relationships:
            if rel["source"] in official_entities and rel["target"] in vendor_entities:
                if rel["relationship_type"] in ["OWNER", "DIRECTOR"]:
                    direct_connections += 1
                else:
                    indirect_connections += 1
        
        # Weight: direct connections are more severe
        total_score = min(100, (direct_connections * 25 + indirect_connections * 10))
        
        return total_score
    
    @staticmethod
    def calculate_family_connection(
        family_relationships: List[Dict[str, Any]],
        entity_id: str
    ) -> float:
        """Calculate family connection score"""
        connection_count = len(family_relationships)
        
        if connection_count == 0:
            return 0
        elif connection_count <= 2:
            return 30
        elif connection_count <= 5:
            return 60
        else:
            return 100
    
    @staticmethod
    def calculate_network_centrality(
        graph_data: Dict[str, Any],
        entity_id: str
    ) -> float:
        """Calculate network centrality score"""
        # Simplified: degree centrality
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        # Count connections for entity
        connection_count = sum(
            1 for e in edges
            if e.get("source") == entity_id or e.get("target") == entity_id
        )
        
        if len(nodes) <= 1:
            return 0
        
        max_possible_connections = len(nodes) - 1
        centrality = connection_count / max_possible_connections if max_possible_connections > 0 else 0
        
        return centrality * 100


class CaseRiskFactors:
    """Risk factors khusus untuk case"""
    
    @staticmethod
    def calculate_evidence_quality(
        evidence_list: List[Dict[str, Any]]
    ) -> float:
        """Calculate evidence quality score"""
        if not evidence_list:
            return 0
        
        # Average trust score of evidence
        trust_scores = [e.get("trust_score", 0) for e in evidence_list]
        avg_trust = sum(trust_scores) / len(trust_scores)
        
        # Weight: more evidence = better quality (up to a point)
        count_bonus = min(20, len(evidence_list) * 2)
        
        return min(100, avg_trust + count_bonus)
    
    @staticmethod
    def calculate_timeline_integrity(
        events: List[Dict[str, Any]]
    ) -> float:
        """Calculate timeline integrity score"""
        if len(events) < 2:
            return 100  # No issue with single event
        
        # Check for gaps in timeline
        total_gap_days = 0
        for i in range(1, len(events)):
            prev_time = events[i-1].get("created_at")
            curr_time = events[i].get("created_at")
            
            if prev_time and curr_time:
                gap = (curr_time - prev_time).days
                if gap > 30:  # More than 30 days gap is suspicious
                    total_gap_days += gap
        
        if total_gap_days <= 0:
            return 100
        elif total_gap_days <= 90:
            return 70
        elif total_gap_days <= 180:
            return 40
        else:
            return 20
    
    @staticmethod
    def calculate_potential_impact(
        estimated_loss: float,
        entity_count: int,
        region_priority: str
    ) -> float:
        """Calculate potential impact score"""
        # Loss impact (max 50 points)
        if estimated_loss >= 1_000_000_000:  # > 1B
            loss_score = 50
        elif estimated_loss >= 500_000_000:   # > 500M
            loss_score = 40
        elif estimated_loss >= 100_000_000:   # > 100M
            loss_score = 30
        elif estimated_loss >= 10_000_000:    # > 10M
            loss_score = 20
        elif estimated_loss >= 1_000_000:     # > 1M
            loss_score = 10
        else:
            loss_score = 5
        
        # Entity impact (max 30 points)
        entity_score = min(30, entity_count * 5)
        
        # Region priority (max 20 points)
        region_scores = {
            "CRITICAL": 20,
            "HIGH": 15,
            "MEDIUM": 10,
            "LOW": 5
        }
        region_score = region_scores.get(region_priority, 10)
        
        return loss_score + entity_score + region_score


class RiskFactorCalculator:
    """Calculator untuk semua risk factors"""
    
    def __init__(self):
        self.vendor_factors = VendorRiskFactors()
        self.entity_factors = EntityRiskFactors()
        self.case_factors = CaseRiskFactors()
    
    def calculate_factor_score(
        self,
        factor: RiskFactor,
        data: Dict[str, Any]
    ) -> float:
        """Calculate score for a specific factor"""
        
        if factor.factor_id == "vendor_dominance":
            return self.vendor_factors.calculate_vendor_dominance(
                package_count=data.get("package_count", 0),
                total_packages=data.get("total_packages", 1),
                total_value=data.get("total_value", 0),
                total_value_all=data.get("total_value_all", 1)
            )
        
        elif factor.factor_id == "bid_rotation":
            return self.vendor_factors.calculate_bid_rotation(
                bid_history=data.get("bid_history", []),
                vendors=data.get("vendors", []),
                packages=data.get("packages", [])
            )
        
        elif factor.factor_id == "single_bidder":
            return self.vendor_factors.calculate_single_bidder_rate(
                single_bidder_packages=data.get("single_bidder_packages", 0),
                total_packages=data.get("total_packages", 1)
            )
        
        elif factor.factor_id == "price_markup":
            return self.vendor_factors.calculate_price_markup(
                contract_price=data.get("contract_price", 0),
                market_price=data.get("market_price", 0),
                reference_price=data.get("reference_price", 0)
            )
        
        elif factor.factor_id == "conflict_of_interest":
            return self.entity_factors.calculate_conflict_of_interest(
                relationships=data.get("relationships", []),
                official_entities=data.get("official_entities", []),
                vendor_entities=data.get("vendor_entities", [])
            )
        
        elif factor.factor_id == "family_connection":
            return self.entity_factors.calculate_family_connection(
                family_relationships=data.get("family_relationships", []),
                entity_id=data.get("entity_id", "")
            )
        
        elif factor.factor_id == "collusion_network":
            return self.entity_factors.calculate_network_centrality(
                graph_data=data.get("graph_data", {}),
                entity_id=data.get("entity_id", "")
            )
        
        elif factor.factor_id == "evidence_quality":
            return self.case_factors.calculate_evidence_quality(
                evidence_list=data.get("evidence_list", [])
            )
        
        elif factor.factor_id == "timeline_integrity":
            return self.case_factors.calculate_timeline_integrity(
                events=data.get("events", [])
            )
        
        elif factor.factor_id == "potential_impact":
            return self.case_factors.calculate_potential_impact(
                estimated_loss=data.get("estimated_loss", 0),
                entity_count=data.get("entity_count", 0),
                region_priority=data.get("region_priority", "MEDIUM")
            )
        
        # Default: use rules if available
        framework = get_risk_framework()
        rules = framework.get_rules_for_factor(factor.factor_id)
        
        for rule in sorted(rules, key=lambda r: r.priority):
            if self._evaluate_condition(rule.condition, data):
                return rule.score
        
        return factor.default_score
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate condition expression safely"""
        try:
            # Simple condition evaluation
            # For production, use a proper expression evaluator like `simpleeval`
            return eval(condition, {"__builtins__": {}}, data)
        except Exception:
            return False


# Singleton instance
_factor_calculator = None

def get_factor_calculator() -> RiskFactorCalculator:
    """Get singleton factor calculator"""
    global _factor_calculator
    if _factor_calculator is None:
        _factor_calculator = RiskFactorCalculator()
    return _factor_calculator