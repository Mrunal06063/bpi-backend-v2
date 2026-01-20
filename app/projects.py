from fastapi import APIRouter, Query
from sqlalchemy import text
from app.database import engine

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

@router.get("")
def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    offset = (page - 1) * limit

    with engine.connect() as conn:
        # Get total number of records
        total_result = conn.execute(
            text("SELECT COUNT(*) FROM projects")
        )
        total_records = total_result.scalar()

        # Get paginated records
        result = conn.execute(
            text("""
                SELECT
                    project_id,
                    project_code,
                    project_name,
                    is_active
                FROM projects
                ORDER BY project_id DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )

        projects = []
        for row in result:
            projects.append({
                "projectId": row.project_id,
                "projectCode": row.project_code,
                "projectName": row.project_name,
                "projectStatus": "Active" if row.is_active else "Inactive"
            })

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
