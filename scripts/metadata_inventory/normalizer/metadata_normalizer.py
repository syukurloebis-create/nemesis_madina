# scripts/metadata_inventory/normalizers/metadata_normalizer.py
from .base import Normalizer
from ..dtos import MetadataDTO, TableDTO, ColumnDTO
from ..raw_models import RawMetadata, RawTable, RawColumn

class MetadataNormalizer(Normalizer):
    """Normalize raw metadata ke MetadataDTO."""
    
    @property
    def name(self) -> str:
        return "metadata"
    
    def normalize(self, raw: 'RawCollection') -> List[MetadataDTO]:
        return [
            self._normalize_one(rm)
            for rm in raw.metadata
        ]
    
    def _normalize_one(self, raw: RawMetadata) -> MetadataDTO:
        return MetadataDTO(
            module=raw.module,
            base_name=raw.base_name,
            metadata_type=raw.metadata_type,
            fingerprint=self._generate_fingerprint(raw),
            tables=self._normalize_tables(raw.tables),
            table_names=[t.fullname for t in raw.tables],
            model_names=[],  # Will be filled from relationships
            mapper_count=raw.mapper_count
        )
    
    def _normalize_tables(self, raw_tables: List[RawTable]) -> List[TableDTO]:
        return [
            TableDTO(
                fullname=rt.fullname,
                columns=[
                    ColumnDTO(
                        name=rc.name,
                        type=rc.type,
                        nullable=rc.nullable,
                        primary_key=rc.primary_key
                    )
                    for rc in rt.columns
                ],
                primary_key=rt.primary_key,
                foreign_keys=rt.foreign_keys,
                indexes=rt.indexes
            )
            for rt in raw_tables
        ]