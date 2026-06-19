# routers/intelligence.py - DEPRECATED (gunakan api/v1/intelligence.py)
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/api/v1/intelligence', tags=['intelligence'], deprecated=True)

@router.get('/')
async def deprecated_root(): 
    raise HTTPException(status_code=410, detail='This endpoint is deprecated. Use /api/v1/intelligence')
