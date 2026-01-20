from fastapi import APIRouter, Query
from sqlalchemy import text
from app.database import engine

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

# =========================
# GET PROJECTS (UNCHANGED)
# =========================
@router.get("")
def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    offset = (page - 1) * limit

    with engine.connect() as conn:
        total_records = conn.execute(
            text("SELECT COUNT(*) FROM projects")
        ).scalar()

        result = conn.execute(
            text("""
                SELECT
                    project_id,
                    project_code,
                    project_name,
                    is_active,
                    remarks
                FROM projects
                ORDER BY project_id DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )

        projects = [
            {
                "projectId": row.project_id,
                "projectCode": row.project_code,
                "projectName": row.project_name,
                "projectStatus": "Active" if row.is_active else "Inactive",
                "remarks": row.remarks
            }
            for row in result
        ]

    total_pages = (total_records + limit - 1) // limit

    return {
        "data": projects,
        "pagination": {
            "currentPage": page,
            "pageSize": limit,
            "totalRecords": total_records,
            "totalPages": total_pages
        }
    }

# =========================
# ADD PROJECT (MATCHES FRONTEND PAYLOAD)
# =========================
@router.post("")
def add_project(payload: dict):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO projects (
                    project_code,
                    project_name,
                    is_active,
                    remarks
                )
                VALUES (
                    :project_code,
                    :project_name,
                    :is_active,
                    :remarks
                )
            """),
            {
                "project_code": payload["projectCode"],
                "project_name": payload["projectName"],
                "is_active": True if payload["projectStatus"] == "Active" else False,
                "remarks": payload.get("remarks")
            }
        )

    return {"message": "Project added successfully"}
