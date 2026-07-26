# scripts/inventory/api.py
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from scripts.inventory.service import InventoryService
from scripts.architecture.logging.logger import NemesisLogger

app = FastAPI(title="NEMESIS Architecture Inventory API", version="1.0.0")
service = InventoryService()
logger = NemesisLogger()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/v1/modules")
async def get_modules(
    type: Optional[str] = Query(None, description="Filter by module type"),
    language: Optional[str] = Query(None, description="Filter by language")
):
    return service.get_modules(type, language)

@app.get("/api/v1/modules/{module_id}")
async def get_module(module_id: str):
    result = service.storage.query("SELECT * FROM modules WHERE id = ?", (module_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Module not found")
    return result[0]

@app.get("/api/v1/relations")
async def get_relations(
    source: Optional[str] = Query(None),
    target: Optional[str] = Query(None)
):
    return service.get_relations(source, target)

@app.get("/api/v1/metrics")
async def get_metrics():
    return {
        "total_modules": service.get_module_count(),
        "legacy_imports": len(service.get_legacy_imports())
    }

@app.get("/api/v1/search")
async def search(q: str = Query(...)):
    """Search using FTS5"""
    result = service.storage.query(
        "SELECT * FROM modules_fts WHERE modules_fts MATCH ?",
        (q,)
    )
    return result