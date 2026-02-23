from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/support", tags=["Support"])

@router.get("/summary")
def support_summary():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT *
        FROM support_tickets
        WHERE date_closed = ""                
    """).fetchall()
    conn.close()
    return {"support_summary": [dict(row) for row in rows]}
