# scripts/architecture/interfaces/i_rule_engine.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from scripts.architecture.models.violation import Violation

class IRuleEngine(ABC):
    """Interface for rule engine"""
    
    @abstractmethod
    def load_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Load rules from configuration"""
        pass
    
    @abstractmethod
    def evaluate(self) -> List[Violation]:
        """Evaluate all rules against inventory"""
        pass
    
    @abstractmethod
    def get_violations(self) -> List[Violation]:
        """Get current violations"""
        pass