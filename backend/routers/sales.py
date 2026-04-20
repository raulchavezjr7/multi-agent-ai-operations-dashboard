from fastapi import APIRouter

from backend.agents.sales_agent import SalesAgent
from backend.database import get_db_connection

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/LLM-summary")
def sales_LMM_summary():
    sales_summary = SalesAgent(model="phi-3.1-mini-4k-instruct").run()
    return sales_summary


@router.get("/summary")
def sales_summary():
    conn = get_db_connection()

    top_10_best_selling_items = conn.execute("""
        SELECT ii.product_id, i.product_name,
            SUM(ii.quantity) AS total_sold
        FROM invoice_item ii
        JOIN inventory i ON ii.product_id = i.product_id
        GROUP BY ii.product_id, i.product_name
        ORDER BY total_sold DESC
        LIMIT 10;
    """).fetchall()

    sales_by_region = conn.execute("""
        SELECT region, SUM(total_amount) AS revenue
        FROM invoice
        GROUP BY region
        ORDER BY revenue DESC;                              
    """).fetchall()

    sales_rep_performance = conn.execute("""
        SELECT sales_rep, SUM(total_amount) AS total_sales
        FROM invoice
        GROUP BY sales_rep
        ORDER BY total_sales DESC;
    """).fetchall()

    top_5_customer_lifetime_value = conn.execute("""
        SELECT c.customer_id, c.name,
            SUM(i.total_amount) AS lifetime_value
        FROM customer c
        JOIN invoice i ON c.customer_id = i.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY lifetime_value DESC                       
        LIMIT 5;
    """).fetchall()

    conn.close()
    return {
        "top_10_best_selling_items": [dict(row) for row in top_10_best_selling_items],
        "sales_by_region": [dict(row) for row in sales_by_region],
        "sales_rep_performance": [dict(row) for row in sales_rep_performance],
        "top_5_customer_lifetime_value": [
            dict(row) for row in top_5_customer_lifetime_value
        ],
    }
