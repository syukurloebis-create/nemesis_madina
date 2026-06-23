# backend/cases/api.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from security import get_current_user, get_current_active_user
from typing import Optional
import logging

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])
logger = logging.getLogger(__name__)

# ... rest of file
