from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from infrastructure.database import AsyncSessionLocal
from sqlalchemy import text
import uuid
import os

router = APIRouter(prefix=/evidence, tags=[evidence])

@router.get(/case/{case_id})
async def get_evidence_by_case(case_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(
