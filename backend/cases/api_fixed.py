# Ganti endpoint create_case dengan ini:

from cases.service import CaseService
from events.types import Event, EventType
from events.event_store import EventStore

@router.post("/")
async def create_case(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"]))
):
    """Create a new case with event sourcing"""
    try:
        body = await request.json()
        title = body.get("title")
        description = body.get("description")
        priority = body.get("priority", "MEDIUM")
        category = body.get("category", "GENERAL")
        institution_id = body.get("institution_id")

        if not title:
            return JSONResponse(status_code=400, content={"error": "title is required"})

        case_id = str(uuid.uuid4())
        user_id = current_user.id if current_user else "system"

        # ==========================================
        # 🔴 FIX: Insert case dengan institution_id
        # ==========================================
        await db.execute(
            text("""
                INSERT INTO cases (id, title, description, status, priority, category, institution_id, created_at, updated_at)
                VALUES (:id, :title, :desc, 'DRAFT', :priority, :category, :inst_id, NOW(), NOW())
            """),
            {
                "id": case_id,
                "title": title,
                "desc": description,
                "priority": priority.upper(),
                "category": category.upper(),
                "inst_id": institution_id
            }
        )

        # ==========================================
        # 🔴 FIX: Create initial event (INI YANG HILANG!)
        # ==========================================
        data = {
            "title": title,
            "description": description or "",
            "priority": priority.upper(),
            "category": category.upper()
        }
        
        await db.execute(
            text("""
                INSERT INTO events (event_id, case_id, event_type, data, timestamp, version, user_id)
                VALUES (:event_id, :case_id, 'case_created', :data, NOW(), 1, :user_id)
            """),
            {
                "event_id": str(uuid.uuid4()),
                "case_id": case_id,
                "data": json.dumps(data),
                "user_id": user_id
            }
        )

        await db.commit()

        return JSONResponse(
            status_code=201,
            content={
                "id": case_id,
                "title": title,
                "status": "DRAFT",
                "message": "Case created with event sourcing"
            }
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
