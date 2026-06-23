"""API Module - Route Aggregator"""

from fastapi import APIRouter

# Import V1 router
from api.v1 import router as v1_router

# Create main router
router = APIRouter()

# Include V1 routes
router.include_router(v1_router)

# Export
__all__ = ["router", "v1_router"]