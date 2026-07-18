# backend/application/commands/analyze_case_command.py
from dataclasses import dataclass
from typing import Optional
from backend.domain.value_objects.case_id import CaseId

@dataclass(frozen=True)
class AnalyzeCaseCommand:
    """Command to analyze a case"""
    case_id: CaseId
    force_refresh: bool = False
    analysis_depth: str = "standard"  # "standard", "deep", "comprehensive"
    metadata: Optional[dict] = None

class AnalyzeCaseCommandHandler:
    """Handler for AnalyzeCaseCommand"""
    
    def __init__(self, case_repository, fraud_engine, intelligence_service):
        self.case_repository = case_repository
        self.fraud_engine = fraud_engine
        self.intelligence_service = intelligence_service
    
    async def handle(self, command: AnalyzeCaseCommand):
        """Handle the command"""
        case = await self.case_repository.get_by_id(command.case_id)
        if not case:
            raise ValueError(f"Case not found: {command.case_id}")
        
        # Run fraud analysis
        fraud_result = await self.fraud_engine.analyze(case)
        
        # Run intelligence analysis
        intelligence_result = await self.intelligence_service.analyze(case)
        
        return {
            'case_id': str(command.case_id),
            'fraud_analysis': fraud_result,
            'intelligence_analysis': intelligence_result,
            'timestamp': datetime.now().isoformat()
        }