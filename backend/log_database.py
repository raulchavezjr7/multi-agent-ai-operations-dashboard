import os
import sqlite3
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = Path(f"{BASE_DIR}/../database/agent_logs.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        agent_role TEXT NOT NULL,
        label TEXT NOT NULL,
        request_type TEXT NOT NULL,
        message_overview TEXT NOT NULL,
        prompt_tokens INT,
        completion_tokens INT,
        details_json TEXT
        );
    """)

    conn.commit()
    conn.close()


init_db()
