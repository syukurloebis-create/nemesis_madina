"""
ORM Mapper - ORM → DTO (IMMUTABLE)
"""

from typing import Any, List, Type, TypeVar
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T')


class OrmMapper:
    """
    Mapper untuk konversi ORM ke DTO.

    HANYA bertanggung jawab untuk ORM → DTO.
    """

    @staticmethod
    def to_dto(model: Any, dto_class: Type[T]) -> T:
        """Konversi ORM model ke DTO."""
        if model is None:
            return None

        field_names = dto_class.__dataclass_fields__.keys()

        kwargs = {}
        for field_name in field_names:
            if hasattr(model, field_name):
                value = getattr(model, field_name)
                # Handle UUID → str conversion jika diperlukan
                if hasattr(value, 'hex') and field_name.endswith('_id'):
                    kwargs[field_name] = str(value)
                else:
                    kwargs[field_name] = value

        return dto_class(**kwargs)

    @staticmethod
    def to_dto_list(models: List[Any], dto_class: Type[T]) -> List[T]:
        """Konversi list ORM model ke list DTO."""
        if not models:
            return []
        return [OrmMapper.to_dto(m, dto_class) for m in models]