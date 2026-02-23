from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/accounting", tags=["Accounting"])

@router.get("/summary")
def accounting_summary():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT strftime('%Y', date) AS year, SUM(amount) AS yearly_total
        FROM accounting
        GROUP BY year               
    """).fetchall()
    conn.close()
    return {"accounting_summary": [dict(row) for row in rows]}
