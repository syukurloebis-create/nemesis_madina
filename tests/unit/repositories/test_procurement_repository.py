# tests/unit/repositories/test_procurement_repository.py

import pytest
from uuid import uuid4
from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.search_options import SearchOptions
from backend.application.dto.procurement_record import ProcurementRecord


class TestProcurementRepository:
    @pytest.mark.asyncio
    async def test_search_empty_criteria(self, repository):
        criteria = InvestigationCriteria.empty(uuid4())
        results = await repository.search(criteria)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_by_institution(self, repository):
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=("KAB. MANDAILING NATAL",),
        )
        results = await repository.search(criteria)
        assert all("MANDAILING NATAL" in r.institution_name for r in results)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_by_vendor(self, repository):
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            vendors=("CV. AULIA RIZKI PRATAMA",),
        )
        results = await repository.search(criteria)
        assert all("CV. AULIA RIZKI PRATAMA" in r.vendor_name for r in results)

    @pytest.mark.asyncio
    async def test_search_by_package(self, repository):
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            packages=("2827373",),
        )
        results = await repository.search(criteria)
        assert all(r.package_code == "2827373" for r in results)

    @pytest.mark.asyncio
    async def test_search_by_year(self, repository):
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            years=(2022,),
        )
        results = await repository.search(criteria)
        assert all(r.year == 2022 for r in results)

    @pytest.mark.asyncio
    async def test_search_combined_filters(self, repository):
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=("KAB. MANDAILING NATAL",),
            years=(2022,),
        )
        results = await repository.search(criteria)
        assert all(
            "MANDAILING NATAL" in r.institution_name and r.year == 2022
            for r in results
        )

    @pytest.mark.asyncio
    async def test_search_with_limit(self, repository):
        criteria = InvestigationCriteria.empty(uuid4())
        results = await repository.search(
            criteria,
            options=SearchOptions(limit=5),
        )
        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_search_order_deterministic(self, repository):
        """Verify ORDER BY produces stable results."""
        criteria = InvestigationCriteria.empty(uuid4())
        results1 = await repository.search(criteria, options=SearchOptions(limit=10))
        results2 = await repository.search(criteria, options=SearchOptions(limit=10))
        assert [r.package_code for r in results1] == [r.package_code for r in results2]

    @pytest.mark.asyncio
    async def test_search_negative_limit_raises(self, repository):
        """Negative limit raises ValueError."""
        criteria = InvestigationCriteria.empty(uuid4())
        with pytest.raises(ValueError, match="limit must be >= 0"):
            await repository.search(criteria, SearchOptions(limit=-1))

    @pytest.mark.asyncio
    async def test_search_negative_offset_raises(self, repository):
        """Negative offset raises ValueError."""
        criteria = InvestigationCriteria.empty(uuid4())
        with pytest.raises(ValueError, match="offset must be >= 0"):
            await repository.search(criteria, SearchOptions(offset=-1))

    @pytest.mark.asyncio
    async def test_search_returns_dto_objects(self, repository):
        """Repository always returns ProcurementRecord objects."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await repository.search(criteria, SearchOptions(limit=5))
        assert all(isinstance(r, ProcurementRecord) for r in results)

    @pytest.mark.asyncio
    async def test_search_order_stable_with_id(self, repository):
        """ORDER BY (year, package_code, id) is stable."""
        criteria = InvestigationCriteria.empty(uuid4())
        results1 = await repository.search(criteria, SearchOptions(limit=50))
        results2 = await repository.search(criteria, SearchOptions(limit=50))
    
        snapshot1 = [(r.year, r.package_code) for r in results1]
        snapshot2 = [(r.year, r.package_code) for r in results2]
        assert snapshot1 == snapshot2