from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/summary")
def sales_summary():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT region, SUM(total_amount) AS revenue
        FROM invoice
        GROUP BY region
    """).fetchall()
    conn.close()
    return {"sales_summary": [dict(row) for row in rows]}
