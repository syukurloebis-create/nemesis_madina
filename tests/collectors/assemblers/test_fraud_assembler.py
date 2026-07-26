"""
Fraud Assembler Unit Test.
"""

import pytest
from datetime import datetime

from backend.collectors.assemblers.fraud_assembler import FraudAssembler
from backend.repositories.rows.fraud_rows import FraudSummaryRow, FraudPatternRow
from backend.domain.enums import Severity, EngineStatus


class TestFraudAssembler:
    """Fraud Assembler Tests."""
    
    def test_assemble_returns_correct_dto(self):
        """Test assembler converts Row to DTO correctly."""
        summary = FraudSummaryRow(
            total_patterns=4,
            critical=1,
            high=2,
            avg_confidence=45.0
        )
        patterns = (
            FraudPatternRow("type1", "HIGH", 80.0, False, datetime.now()),
            FraudPatternRow("type2", "MEDIUM", 60.0, False, None),
        )
        
        result = FraudAssembler.assemble(summary, patterns)
        
        assert result.total_patterns == 4
        assert result.critical == 1
        assert result.high == 2
        assert len(result.patterns) == 2
        assert result.patterns[0].severity == Severity.HIGH
    
    def test_assemble_empty(self):
        """Test assemble_empty returns empty DTO."""
        result = FraudAssembler.assemble_empty()
        
        assert result.total_patterns == 0
        assert result.engine_status == EngineStatus.OK
