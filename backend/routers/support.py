from fastapi import APIRouter

from backend.agents.support_agent import SupportAgent
from backend.database import get_db_connection

router = APIRouter(prefix="/support", tags=["Support"])


@router.get("/LLM-summary")
def support_LMM_summary():
    support_summary = SupportAgent(model="phi-3.1-mini-4k-instruct").run()
    return support_summary


@router.get("/summary")
def support_summary():
    conn = get_db_connection()
    tickets_by_status = conn.execute("""
        SELECT status, COUNT(*) AS ticket_count
        FROM support_tickets
        GROUP BY status;  
    """).fetchall()

    average_resolution_time_by_priority = conn.execute("""
        SELECT priority, AVG(resolution_time_hours) AS avg_resolution
        FROM support_tickets
        GROUP BY priority
        ORDER BY avg_resolution ASC;
    """).fetchall()

    tickets_per_customer_top_10 = conn.execute("""
        SELECT customer_id, COUNT(*) AS ticket_count
        FROM support_tickets
        GROUP BY customer_id
        ORDER BY ticket_count DESC
        LIMIT 10;                                
    """).fetchall()

    tickets_per_category = conn.execute("""
        SELECT category, COUNT(*) AS ticket_count
        FROM support_tickets
        GROUP BY category
        ORDER BY ticket_count DESC; 
    """).fetchall()

    sentiment_analysis_summary = conn.execute("""
        SELECT customer_sentiment, COUNT(*) AS count
        FROM support_tickets
        GROUP BY customer_sentiment
        ORDER BY count DESC; 
    """).fetchall()

    conn.close()
    return {
        "tickets_by_status": [dict(row) for row in tickets_by_status],
        "average_resolution_time_by_priority": [
            dict(row) for row in average_resolution_time_by_priority
        ],
        "tickets_per_customer_top_10": [
            dict(row) for row in tickets_per_customer_top_10
        ],
        "tickets_per_category": [dict(row) for row in tickets_per_category],
        "sentiment_analysis_summary": [dict(row) for row in sentiment_analysis_summary],
    }
