# tests/integration/repositories/test_procurement_search_integration.py

import pytest
from uuid import uuid4
from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.search_options import SearchOptions
from backend.application.dto.procurement_record import ProcurementRecord
from tests.fixtures.procurement.constants import (
    DEFAULT_PAGE_SIZE,
    LARGE_PAGE_SIZE,
    OFFSET_BEYOND_DATA,
    UNKNOWN_INSTITUTION,
    NON_EXISTENT_YEAR,
)
from tests.fixtures.procurement.datasets import (
    get_small_dataset,
    get_small_dataset_by_code,
)
from tests.fixtures.procurement.filters import (
    filter_dataset,
    filter_dataset_any,
)
from tests.fixtures.procurement.expectations import (
    build_expected_package_codes,
    build_expected_order,
    build_expected_counts,
)
from tests.fixtures.procurement.sorting import visible_sort_key


@pytest.mark.integration
@pytest.mark.asyncio
class TestProcurementSearchIntegration:
    """Repository integration tests - WITH SEEDED DATA."""

    async def test_search_empty_criteria_returns_all(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Search with empty criteria returns all seeded records."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria)

        dataset = get_small_dataset()
        assert len(results) == len(dataset)
        package_codes = {r.package_code for r in results}
        assert set(build_expected_package_codes(dataset)) == package_codes

    async def test_search_by_institution(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Search by single institution filters correctly."""
        dataset = get_small_dataset()
        first = dataset[0]
        institution = first["nama_instansi"]

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=(institution,),
        )
        results = await search_repository.search(criteria)

        assert all(institution in r.institution_name for r in results)
        expected = filter_dataset(nama_instansi=institution)
        assert len(results) == len(expected)

    async def test_search_by_multiple_institutions(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Search by multiple institutions filters correctly."""
        dataset = get_small_dataset()
        institutions = (dataset[0]["nama_instansi"], dataset[2]["nama_instansi"])

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=institutions,
        )
        results = await search_repository.search(criteria)

        expected = filter_dataset_any(nama_instansi=institutions)
        assert len(results) == len(expected)

    async def test_search_by_vendor(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Search by vendor filters correctly."""
        dataset = get_small_dataset()
        first = dataset[0]
        vendor = first["nama_penyedia"]

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            vendors=(vendor,),
        )
        results = await search_repository.search(criteria)

        assert all(vendor in r.vendor_name for r in results)
        expected_counts = build_expected_counts(dataset, "nama_penyedia")
        assert len(results) == expected_counts[vendor]

    async def test_search_by_package(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Search by package code filters correctly."""
        dataset = get_small_dataset()
        first = dataset[0]
        package = first["kode_paket"]

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            packages=(package,),
        )
        results = await search_repository.search(criteria)

        assert len(results) == 1
        assert results[0].package_code == package

    async def test_search_by_year(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Search by year filters correctly."""
        dataset = get_small_dataset()
        first = dataset[0]
        year = first["tahun_anggaran"]

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            years=(year,),
        )
        results = await search_repository.search(criteria)

        assert all(r.year == year for r in results)
        expected = filter_dataset(tahun_anggaran=year)
        assert len(results) == len(expected)

    async def test_search_combined_filters(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Combined filters work correctly."""
        dataset = get_small_dataset()
        first = dataset[0]
        institution = first["nama_instansi"]
        year = first["tahun_anggaran"]

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=(institution,),
            years=(year,),
        )
        results = await search_repository.search(criteria)

        assert all(institution in r.institution_name for r in results)
        assert all(r.year == year for r in results)

        expected = filter_dataset(nama_instansi=institution, tahun_anggaran=year)
        assert len(results) == len(expected)

    async def test_search_with_limit(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Limit restricts results."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria, SearchOptions(limit=DEFAULT_PAGE_SIZE))
        assert len(results) == DEFAULT_PAGE_SIZE

    async def test_search_with_limit_greater_than_data(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Limit > data count returns all data."""
        criteria = InvestigationCriteria.empty(uuid4())
        dataset = get_small_dataset()
        results = await search_repository.search(criteria, SearchOptions(limit=LARGE_PAGE_SIZE))
        assert len(results) == len(dataset)

    async def test_search_with_offset(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Offset pagination works."""
        criteria = InvestigationCriteria.empty(uuid4())
        first = await search_repository.search(criteria, SearchOptions(limit=DEFAULT_PAGE_SIZE, offset=0))
        second = await search_repository.search(criteria, SearchOptions(limit=DEFAULT_PAGE_SIZE, offset=DEFAULT_PAGE_SIZE))

        assert len(first) == DEFAULT_PAGE_SIZE
        assert len(second) == DEFAULT_PAGE_SIZE
        assert first[0].package_code != second[0].package_code

    async def test_search_with_offset_beyond_data(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Offset beyond data returns empty list."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria, SearchOptions(limit=DEFAULT_PAGE_SIZE, offset=OFFSET_BEYOND_DATA))
        assert len(results) == 0

    async def test_search_order_deterministic(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """ORDER BY (year, package_code) is stable."""
        criteria = InvestigationCriteria.empty(uuid4())
        results = await search_repository.search(criteria, SearchOptions(limit=10))

        dataset = get_small_dataset()
        expected_order = build_expected_order(dataset, visible_sort_key)
        actual_order = [r.package_code for r in results]
        assert actual_order == expected_order

    async def test_search_unknown_institution(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Unknown filter returns empty list."""
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=(UNKNOWN_INSTITUTION,),
        )
        results = await search_repository.search(criteria)
        assert len(results) == 0

    async def test_search_empty_combination(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """Empty combination returns empty list."""
        criteria = InvestigationCriteria(
            case_id=uuid4(),
            institutions=(UNKNOWN_INSTITUTION,),
            years=(NON_EXISTENT_YEAR,),
        )
        results = await search_repository.search(criteria)
        assert len(results) == 0

    async def test_dto_mapping(
        self,
        search_repository,
        seed_small_procurement_dataset,
    ):
        """DTO mapping is correct."""
        dataset = get_small_dataset()
        first = dataset[0]
        package = first["kode_paket"]

        criteria = InvestigationCriteria(
            case_id=uuid4(),
            packages=(package,),
        )
        results = await search_repository.search(criteria)

        assert len(results) == 1
        record = results[0]
        assert isinstance(record, ProcurementRecord)

        expected = get_small_dataset_by_code(package)
        assert expected is not None

        assert record.package_code == expected["kode_paket"]
        assert record.package_name == expected["nama_paket"]
        assert record.institution_name == expected["nama_instansi"]
        assert record.vendor_name == expected["nama_penyedia"]
        assert record.year == expected["tahun_anggaran"]
        assert record.value == expected["total_nilai"]
        assert record.status == expected["status_paket"]