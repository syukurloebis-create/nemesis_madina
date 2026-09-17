# tests/unit/repositories/test_procurement_search_contract.py

import pytest
from uuid import uuid4
from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.search_options import SearchOptions
from backend.application.dto.procurement_record import ProcurementRecord


@pytest.mark.asyncio
class TestProcurementSearchContract:
    """Repository contract tests - NO DATA ASSUMPTIONS."""

    async def test_search_returns_list(self, search_repository):
        """Contract: search always returns a list."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria)
        assert isinstance(results, list)

    async def test_search_returns_procurement_records(self, search_repository):
        """Contract: results are ProcurementRecord objects."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria)
        if results:
            assert all(isinstance(r, ProcurementRecord) for r in results)

    async def test_search_with_default_options(self, search_repository):
        """Contract: search without options equals search with default options."""
        criteria = InvestigationCriteria.empty(uuid4())
        results1 = await search_repository.search(criteria)
        results2 = await search_repository.search(criteria, SearchOptions())
        assert len(results1) == len(results2)

    async def test_search_empty_criteria_no_exception(self, search_repository):
        """Contract: empty criteria does not raise exception."""
        criteria = InvestigationCriteria.empty(uuid4())
        try:
            await search_repository.search(criteria)
        except Exception as e:
            pytest.fail(f"Empty criteria should not raise: {e}")

    async def test_search_with_limit(self, search_repository):
        """Contract: limit works even with empty data."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria, SearchOptions(limit=5))
        assert isinstance(results, list)
        assert len(results) <= 5

    async def test_search_with_negative_limit_raises(self, search_repository):
        """Contract: negative limit raises ValueError."""
        criteria = InvestigationCriteria.empty(uuid4())
        with pytest.raises(ValueError, match="limit must be >= 0"):
            await search_repository.search(criteria, SearchOptions(limit=-1))

    async def test_search_with_negative_offset_raises(self, search_repository):
        """Contract: negative offset raises ValueError."""
        criteria = InvestigationCriteria.empty(uuid4())
        with pytest.raises(ValueError, match="offset must be >= 0"):
            await search_repository.search(criteria, SearchOptions(offset=-1))

    async def test_search_with_unknown_institution(self, search_repository):
        """Contract: unknown filters return empty list."""
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=("UNKNOWN_INSTITUTION",),
        )
        results = await search_repository.search(criteria)
        assert isinstance(results, list)
        assert len(results) == 0

    async def test_search_with_limit_greater_than_data(self, search_repository):
        """Contract: limit > data count returns all available data."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria, SearchOptions(limit=100))
        assert isinstance(results, list)

    async def test_search_empty_combination_returns_empty(self, search_repository):
        """Contract: empty combination returns empty list."""
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=("UNKNOWN",),
            years=(2050,),
        )
        results = await search_repository.search(criteria)
        assert isinstance(results, list)
        assert len(results) == 0