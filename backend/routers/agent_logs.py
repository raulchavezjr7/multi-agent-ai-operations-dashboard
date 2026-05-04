from typing import Optional

from fastapi import APIRouter, Query

from backend.log_database import get_connection

router = APIRouter(prefix="/agent-logs", tags=["Agent Logs"])


@router.get("/")
def list_logs(
    agent_name: Optional[str] = None,
    label: Optional[str] = None,
    request_type: Optional[str] = None,
    limit: int = Query(200, le=1000),
):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM agent_logs WHERE 1=1"
    params = []

    if agent_name:
        query += " AND agent_name = ?"
        params.append(agent_name)

    if label:
        query += " AND label = ?"
        params.append(label)

    if request_type:
        query += " AND request_type = ?"
        params.append(request_type)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
