from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/operations", tags=["Operations"])

@router.get("/summary")
def operations_summary():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT region, COUNT(customer_id) AS total_customers
        FROM customer
        GROUP BY region    
    """).fetchall()
    conn.close()
    return {"operations_summary": [dict(row) for row in rows]}
