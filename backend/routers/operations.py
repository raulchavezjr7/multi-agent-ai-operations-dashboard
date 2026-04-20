from fastapi import APIRouter

from backend.agents.operations_agent import OperationsAgent
from backend.database import get_db_connection

router = APIRouter(prefix="/operations", tags=["Operations"])


@router.get("/LLM-summary")
def operations_LMM_summary():
    operations_summary = OperationsAgent(model="phi-3.1-mini-4k-instruct").run()
    return operations_summary


@router.get("/summary")
def operations_summary():
    conn = get_db_connection()

    customer_count_by_region = conn.execute("""
        SELECT region, COUNT(customer_id) AS total_customers
        FROM customer
        GROUP BY region    
    """).fetchall()

    customer_value_tier_by_industry = conn.execute("""
        SELECT 
            industry,
            ROUND(100.0 * SUM(CASE WHEN customer_value_tier = 'Gold' THEN 1 ELSE 0 END) / COUNT(*), 2) AS gold_pct,
            ROUND(100.0 * SUM(CASE WHEN customer_value_tier = 'Silver' THEN 1 ELSE 0 END) / COUNT(*), 2) AS silver_pct,
            ROUND(100.0 * SUM(CASE WHEN customer_value_tier = 'Bronze' THEN 1 ELSE 0 END) / COUNT(*), 2) AS bronze_pct,
            COUNT(*) AS total_customers
        FROM customer
        GROUP BY industry
        ORDER BY gold_pct DESC;
    """).fetchall()

    top_5_customers_by_invoice_total = conn.execute("""
        SELECT c.customer_id, c.name, SUM(i.total_amount) AS total_spent
        FROM customer c
        JOIN invoice i ON c.customer_id = i.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT 5;   
    """).fetchall()

    customer_churn_risk = conn.execute("""
        SELECT c.customer_id, c.name, MAX(i.invoice_date) AS last_invoice
        FROM customer c
        LEFT JOIN invoice i ON c.customer_id = i.customer_id
        GROUP BY c.customer_id, c.name
        HAVING MAX(i.invoice_date) < date('now', '-12 months')
        OR MAX(i.invoice_date) IS NULL;
    """).fetchall()

    conn.close()
    return {
        "customer_count_by_region": [dict(row) for row in customer_count_by_region],
        "customer_value_tier_by_industry": [
            dict(row) for row in customer_value_tier_by_industry
        ],
        "top_5_customers_by_invoice_total": [
            dict(row) for row in top_5_customers_by_invoice_total
        ],
        "customer_churn_risk": [dict(row) for row in customer_churn_risk],
    }
