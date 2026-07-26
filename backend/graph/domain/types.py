# backend/graph/domain/types.py

"""
Graph Domain Types - Enums for graph domain.

No ORM dependencies. Pure domain.
"""

from enum import Enum


class NodeType(str, Enum):
    """Node types in graph domain."""
    ENTITY = "entity"
    USER = "user"
    VENDOR = "vendor"
    OFFICIAL = "official"
    COMPANY = "company"
    PERSON = "person"
    ACCOUNT = "account"
    ADDRESS = "address"
    BANK_ACCOUNT = "bank_account"
    PROCUREMENT = "procurement"


class EdgeType(str, Enum):
    """Edge types in graph domain."""
    INTERACTS = "interacts"
    TRANSACTION = "transaction"
    COLLUSION = "collusion"
    OWNER = "owner"
    DIRECTOR = "director"
    SHAREHOLDER = "shareholder"
    FAMILY = "family"
    SAME_ADDRESS = "same_address"
    SAME_PHONE = "same_phone"
    SAME_BANK_ACCOUNT = "same_bank_account"
    PROCUREMENT_PARTICIPANT = "procurement_participant"
    CONTRACT_SIGNATORY = "contract_signatory"
    FINANCIAL = "financial"
    SHARED_OWNERSHIP = "shared_ownership"