from fastapi import APIRouter

from backend.agents.accounting_agent import AccountingAgent
from backend.database import get_db_connection

router = APIRouter(prefix="/accounting", tags=["Accounting"])


@router.get("/LLM-summary")
def accounting_LMM_summary():
    accounting_summary = AccountingAgent(model="phi-3.1-mini-4k-instruct").run()
    return accounting_summary


@router.get("/summary")
def accounting_summary():
    conn = get_db_connection()
    payment_method_distribution = conn.execute("""
        SELECT payment_method, COUNT(*) AS count
        FROM invoice
        GROUP BY payment_method
        ORDER BY count DESC;
    """).fetchall()

    top_10_customers_by_profit = conn.execute("""
        SELECT 
            c.customer_id,
            c.name,
            SUM(ii.quantity * ii.unit_price) AS revenue,
            SUM(ii.quantity * inv.unit_cost) AS cogs,
            SUM(ii.quantity * (ii.unit_price - inv.unit_cost)) AS profit
        FROM customer c
        JOIN invoice i ON c.customer_id = i.customer_id
        JOIN invoice_item ii ON i.invoice_id = ii.invoice_id
        JOIN inventory inv ON ii.product_id = inv.product_id
        GROUP BY c.customer_id, c.name
        ORDER BY profit DESC
        Limit 10;
    """).fetchall()

    total_expense_by_department = conn.execute("""
        SELECT department, SUM(amount) AS total_spent
        FROM accounting
        WHERE account != 'Revenue'
        GROUP BY department
        ORDER BY total_spent DESC;                            
    """).fetchall()

    profit_margin = conn.execute("""
        SELECT
            SUM(CASE WHEN account = 'Revenue' THEN amount ELSE 0 END) AS revenue,
            SUM(CASE WHEN account != 'Revenue' THEN amount ELSE 0 END) AS expenses,
            (SUM(CASE WHEN account = 'Revenue' THEN amount ELSE 0 END) -
            SUM(CASE WHEN account != 'Revenue' THEN amount ELSE 0 END)) AS profit,
            ROUND(
                (SUM(CASE WHEN account = 'Revenue' THEN amount ELSE 0 END) -
                SUM(CASE WHEN account != 'Revenue' THEN amount ELSE 0 END))
                / NULLIF(SUM(CASE WHEN account = 'Revenue' THEN amount ELSE 0 END), 0)
                * 100, 2
            ) AS profit_margin_percent
        FROM accounting;
    """).fetchall()

    conn.close()
    return {
        "payment_method_distribution": [
            dict(row) for row in payment_method_distribution
        ],
        "top_10_customers_by_profit": [dict(row) for row in top_10_customers_by_profit],
        "total_expense_by_department": [
            dict(row) for row in total_expense_by_department
        ],
        "profit_margin": [dict(row) for row in profit_margin],
    }
