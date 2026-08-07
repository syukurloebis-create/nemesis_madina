# scripts/metadata_inventory/collectors/sqlalchemy_collector.py
from .base import Collector
from ..raw_models import RawMetadata, RawTable, RawColumn, RawCollection

class SQLAlchemyCollector(Collector):
    """Collector untuk SQLAlchemy (output RawCollection)."""
    
    @property
    def name(self) -> str:
        return "sqlalchemy"
    
    def collect(self, context) -> RawCollection:
        """Kumpulkan data dari SQLAlchemy tanpa expose ke layer atas."""
        raw_metadata = []
        raw_relationships = []
        raw_foreign_keys = []
        
        for module_path, base_name in context.get("bases", []):
            module, base = self._safe_import(module_path, base_name)
            if not base:
                continue
            
            # Kumpulkan metadata
            raw_metadata.append(self._collect_metadata(module_path, base))
            
            # Kumpulkan relationships
            raw_relationships.extend(self._collect_relationships(module_path, base))
            
            # Kumpulkan foreign keys
            raw_foreign_keys.extend(self._collect_foreign_keys(base))
        
        return RawCollection(
            metadata=raw_metadata,
            relationships=raw_relationships,
            foreign_keys=raw_foreign_keys
        )
    
    def _collect_metadata(self, module: str, base) -> RawMetadata:
        """Collect raw metadata tanpa SQLAlchemy exposure."""
        tables = []
        for table in base.metadata.tables.values():
            columns = [
                RawColumn(
                    name=col.name,
                    type=str(col.type),
                    nullable=col.nullable,
                    primary_key=col.primary_key,
                    default=str(col.default) if col.default else None
                )
                for col in table.columns
            ]
            
            fks = [
                {"source": f"{fk.parent.table.fullname}.{fk.parent.name}",
                 "target": f"{fk.column.table.fullname}.{fk.column.name}"}
                for fk in table.foreign_keys
            ]
            
            indexes = [
                {"name": idx.name,
                 "columns": [col.name for col in idx.columns],
                 "unique": idx.unique}
                for idx in table.indexes
            ]
            
            tables.append(RawTable(
                fullname=table.fullname,
                columns=columns,
                primary_key=[col.name for col in table.primary_key.columns] if table.primary_key else [],
                foreign_keys=fks,
                indexes=indexes
            ))
        
        return RawMetadata(
            module=module,
            base_name="Base",
            metadata_type=type(base.metadata).__name__,
            tables=tables,
            mapper_count=len(base.registry.mappers) if hasattr(base, 'registry') else 0
        )