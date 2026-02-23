from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/summary")
def inventory_summary():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT SUM(unit_price * current_stock) AS total_value
        FROM inventory
    """).fetchall()
    conn.close()
    return {"inventory_summary": [dict(row) for row in rows]}
