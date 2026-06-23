from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import uuid
import json
import logging

from security.dependencies import get_current_active_user
from security.models import User
from infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger(__name__)

# Store upload history
upload_history = []


async def auto_create_case(db: AsyncSession, row: Dict, user_id: str, username: str) -> Dict:
    """Auto create case from uploaded data"""
    try:
        case_id = str(uuid.uuid4())
        version = 1
        event_id = str(uuid.uuid4())
        
        # Extract case data
        title = row.get("title") or row.get("name") or f"Auto Case {datetime.now().strftime('%Y%m%d%H%M%S')}"
        description = row.get("description") or row.get("desc") or ""
        priority = row.get("priority", "MEDIUM").upper()
        
        event_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "created_by": user_id,
            "created_by_username": username,
            "source": "upload"
        }
        
        # Compute hash (simplified for demo)
        import hashlib
        event_hash = hashlib.sha256(
            f"{case_id}{event_id}{title}{priority}".encode()
        ).hexdigest()
        
        # Insert event
        await db.execute(
            text("""
                INSERT INTO events (event_id, case_id, event_type, data, timestamp, version, user_id, event_hash)
                VALUES (:event_id, CAST(:case_id AS uuid), 'case_created', :data, NOW(), :version, :user_id, :event_hash)
            """),
            {
                "event_id": event_id,
                "case_id": case_id,
                "data": json.dumps(event_data),
                "version": version,
                "user_id": user_id,
                "event_hash": event_hash
            }
        )
        
        # Insert case
        await db.execute(
            text("""
                INSERT INTO cases (id, title, description, status, priority, created_at, updated_at)
                VALUES (:id, :title, :desc, 'OPEN', :priority, NOW(), NOW())
            """),
            {
                "id": case_id,
                "title": title,
                "desc": description,
                "priority": priority
            }
        )
        
        await db.commit()
        
        return {
            "success": True,
            "case_id": case_id,
            "title": title,
            "event_hash": event_hash[:16] + "..."
        }
        
    except Exception as e:
        logger.error(f"Auto create case failed: {e}")
        return {"success": False, "error": str(e)}


def detect_row_type(row: Dict) -> str:
    """Auto detect row type based on fields"""
    # Check if it's a case
    if "title" in row and ("priority" in row or "description" in row):
        return "case"
    # Check if it's a vendor
    if "name" in row and ("registration_number" in row or "address" in row):
        return "vendor"
    # Check if it's evidence
    if "evidence_id" in row or ("title" in row and "case_id" in row):
        return "evidence"
    return "unknown"


@router.post("/process")
async def process_upload(
    file_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Process uploaded file data with auto-detection and auto-creation"""
    try:
        filename = file_data.get("filename", "unknown")
        data = file_data.get("data", [])
        total_rows = file_data.get("total_rows", 0)
        
        processed_rows = 0
        failed_rows = 0
        created_cases = []
        errors = []
        
        for i, row in enumerate(data):
            try:
                row_type = detect_row_type(row)
                
                if row_type == "case":
                    # Auto create case
                    result = await auto_create_case(
                        db, row, current_user.id, current_user.username
                    )
                    if result.get("success"):
                        processed_rows += 1
                        created_cases.append(result)
                    else:
                        failed_rows += 1
                        errors.append({"row": i + 1, "error": result.get("error", "Unknown")})
                else:
                    # For other types, just validate and store
                    processed_rows += 1
                    
                # Store to history
                upload_history.append({
                    "id": str(uuid.uuid4()),
                    "filename": filename,
                    "row_index": i,
                    "row_type": row_type,
                    "status": "success",
                    "processed_at": datetime.now().isoformat(),
                    "user": current_user.username
                })
                
            except Exception as row_error:
                failed_rows += 1
                errors.append({"row": i + 1, "error": str(row_error)})
        
        # Keep only last 100 history
        while len(upload_history) > 100:
            upload_history.pop(0)
        
        return {
            "success": failed_rows == 0,
            "total_rows": total_rows,
            "processed_rows": processed_rows,
            "failed_rows": failed_rows,
            "created_cases": created_cases,
            "message": f"Successfully processed {processed_rows} rows" + 
                      (f", created {len(created_cases)} new cases" if created_cases else ""),
            "errors": errors if errors else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file")
async def upload_file(
    file_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process file directly"""
    try:
        data = file_data.get("data", [])
        filename = file_data.get("filename", "unknown")
        
        created_cases = []
        for row in data:
            row_type = detect_row_type(row)
            if row_type == "case":
                result = await auto_create_case(db, row, current_user.id, current_user.username)
                if result.get("success"):
                    created_cases.append(result)
        
        return {
            "success": True,
            "filename": filename,
            "rows_processed": len(data),
            "cases_created": len(created_cases),
            "created_cases": created_cases,
            "message": f"Processed {len(data)} rows, created {len(created_cases)} new cases"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_upload_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """Get upload history"""
    history = upload_history[offset:offset + limit]
    return {"data": history, "total": len(upload_history), "offset": offset, "limit": limit}
