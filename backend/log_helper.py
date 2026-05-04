import json
from datetime import datetime

from backend.log_database import get_connection


def log_agent_event(
    agent_name: str,
    agent_role: str,
    label: str,
    request_type: str,
    message_overview: str,
    prompt_tokens: int,
    completion_tokens: int,
    details: dict | None = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO agent_logs (timestamp, agent_name, agent_role, label, request_type, message_overview, prompt_tokens, completion_tokens, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.utcnow().isoformat(),
            agent_name,
            agent_role,
            label,
            request_type,
            message_overview,
            prompt_tokens,
            completion_tokens,
            json.dumps(details) if details else None,
        ),
    )

    conn.commit()
    conn.close()
