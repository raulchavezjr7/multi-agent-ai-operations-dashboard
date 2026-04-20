from fastapi import APIRouter

from backend.agents.inventory_agent import InventoryAgent
from backend.database import get_db_connection

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/LLM-summary")
def inventory_LMM_summary():
    inventory_summary = InventoryAgent(model="phi-3.1-mini-4k-instruct").run()
    return inventory_summary


@router.get("/summary")
def inventory_summary():
    conn = get_db_connection()
    inventory_by_category = conn.execute("""
        SELECT category, SUM(current_stock) AS total_stock
        FROM inventory
        GROUP BY category
        ORDER BY total_stock DESC;   
    """).fetchall()

    low_stock_items = conn.execute("""
        SELECT product_id, product_name, current_stock, reorder_level
        FROM inventory
        WHERE current_stock < reorder_level
        ORDER BY current_stock ASC;  
    """).fetchall()

    inventory_value_by_category = conn.execute("""
        SELECT category, SUM(current_stock * unit_cost) AS inventory_value
        FROM inventory
        GROUP BY category
        ORDER BY inventory_value DESC; 
    """).fetchall()

    top_5_products_with_highest_markup = conn.execute("""
        SELECT product_id, product_name, unit_cost, unit_price,
            (unit_price - unit_cost) AS margin
        FROM inventory
        ORDER BY margin DESC
        LIMIT 5;  
    """).fetchall()

    conn.close()
    return {
        "inventory_by_category": [dict(row) for row in inventory_by_category],
        "low_stock_items": [dict(row) for row in low_stock_items],
        "inventory_value_by_category": [
            dict(row) for row in inventory_value_by_category
        ],
        "top_5_products_with_highest_markup": [
            dict(row) for row in top_5_products_with_highest_markup
        ],
    }
