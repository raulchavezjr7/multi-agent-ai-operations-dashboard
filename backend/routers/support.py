from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/support", tags=["Support"])


@router.get("/summary")
def support_summary():
    conn = get_db_connection()

    total_open = conn.execute("""
         SELECT COUNT(*) AS count
         FROM support_tickets
         WHERE date_closed = ""
    """).fetchone()["count"]

    common_issues = conn.execute("""
        SELECT category, COUNT(*) AS count
        FROM support_tickets WHERE date_closed = ""
        GROUP BY category
        ORDER BY count
        DESC LIMIT 5 
    """).fetchall()

    priority_counts = conn.execute("""
        SELECT priority, COUNT(*) AS count
        FROM support_tickets
        WHERE date_closed = ""
        GROUP BY priority
    """).fetchall()

    sample_tickets = conn.execute("""
        SELECT customer_id, category, priority, ticket_description
        FROM support_tickets
        WHERE date_closed = "" LIMIT 10
    """).fetchall()

    conn.close()
    return {
        "total_open_tickets": total_open,
        "top_issues": [dict(row) for row in common_issues],
        "tickets_by_priority": [dict(row) for row in priority_counts],
        "sample_tickets": [dict(row) for row in sample_tickets],
    }
