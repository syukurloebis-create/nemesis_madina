# main.py - Nemesis Backend (CLEAN - SINGLE ROUTER)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nemesis Intelligence API",
    description="Strategic Intelligence Center",
    version="8.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REGISTER V1 ROUTER (SINGLE ENTRY POINT)
# ============================================
try:
    from backend.api.v1 import router as v1_router
    app.include_router(v1_router)
    logger.info("✅ V1 Router registered")
except Exception as e:
    logger.error(f"❌ Failed to register V1 router: {e}")

# ============================================
# ROOT ENDPOINTS
# ============================================
@app.get("/")
async def root():
    return {
        "name": "Nemesis Intelligence API",
        "version": "8.0.0",
        "status": "operational",
        "docs": "/docs",
        "api": "/api/v1"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nemesis-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
