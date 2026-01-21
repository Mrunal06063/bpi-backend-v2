from fastapi import APIRouter, Query, Depends
from sqlalchemy import text
from app.database import engine
from app.utils.auth_guard import get_current_user

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

# =========================
# GET PROJECTS (JWT PROTECTED)
# =========================
@router.get("")
def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    user=Depends(get_current_user)
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
                    status,
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
                "projectStatus": row.status,
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
# ADD PROJECT (JWT PROTECTED)
# =========================
@router.post("")
def add_project(
    payload: dict,
    user=Depends(get_current_user)
):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO projects (
                    project_code,
                    project_name,
                    status,
                    remarks
                )
                VALUES (
                    :project_code,
                    :project_name,
                    :status,
                    :remarks
                )
            """),
            {
                "project_code": payload["projectCode"],
                "project_name": payload["projectName"],
                "status": payload.get("projectStatus", "Active"),
                "remarks": payload.get("remarks")
            }
        )

    return {"message": "Project added successfully"}


# =========================
# UPDATE PROJECT STATUS (JWT PROTECTED)
# =========================
@router.patch("/{project_id}/status")
def update_project_status(
    project_id: int,
    payload: dict,
    user=Depends(get_current_user)
):
    status = payload.get("status", "Active")

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE projects
                SET status = :status
                WHERE project_id = :project_id
            """),
            {
                "status": status,
                "project_id": project_id
            }
        )

        if result.rowcount == 0:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Project not found")

    return {"message": "Project status updated successfully"}
