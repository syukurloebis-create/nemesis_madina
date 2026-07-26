"""
NEMESIS Madina - BaseUUID Tests
"""

import pytest
from uuid import UUID, uuid4

from backend.domain.value_objects.base_uuid import BaseUUID


class TestBaseUUID:
    def test_generate_creates_valid_uuid(self):
        uuid_obj = BaseUUID.generate()
        assert isinstance(uuid_obj.value, UUID)
        assert str(uuid_obj.value) != ""
    
    def test_from_string_creates_valid_uuid(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        uuid_obj = BaseUUID.from_string(uuid_str)
        assert str(uuid_obj.value) == uuid_str
    
    def test_equality_works(self):
        uuid1 = BaseUUID.generate()
        uuid2 = BaseUUID.from_string(str(uuid1.value))
        assert uuid1 == uuid2
    
    def test_hash_works(self):
        uuid1 = BaseUUID.generate()
        uuid2 = BaseUUID.from_string(str(uuid1.value))
        assert hash(uuid1) == hash(uuid2)
    
    def test_to_dict_returns_string(self):
        uuid_obj = BaseUUID.generate()
        assert uuid_obj.to_dict() == str(uuid_obj.value)