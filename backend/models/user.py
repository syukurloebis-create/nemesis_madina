# backend/models/user.py - COMPATIBILITY LAYER

"""
User Models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from backend.security.models import User
from backend.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    VIEWER = "viewer"
    AUDITOR = "auditor"

__all__ = ["User", "UserRole"]