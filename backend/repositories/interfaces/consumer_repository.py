"""
Consumer Repository Interface — Konsisten dengan repository lain.

NOTE: Semua repository yang menerima case_id harus memiliki kontrak yang sama.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from backend.repositories.rows.consumer_rows import ConsumerSummaryRow


class IConsumerRepository(ABC):
    """
    Consumer Repository Interface.
    
    NOTE: Data consumer adalah PER CASE (memiliki case_id).
    """
    
    @abstractmethod
    async def get_summary(self, case_id: UUID) -> ConsumerSummaryRow:
        """
        Get consumer summary for a case.
        
        Args:
            case_id: UUID of the case
        
        Returns:
            ConsumerSummaryRow: Typed row object
        """
        pass