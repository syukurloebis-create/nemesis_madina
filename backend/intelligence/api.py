# intelligence/api.py - DEPRECATED
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/intelligence', tags=['Intelligence'], deprecated=True)

@router.get('/')
async def deprecated_root(): 
    raise HTTPException(status_code=410, detail='This endpoint is deprecated. Use /api/v1/intelligence')
