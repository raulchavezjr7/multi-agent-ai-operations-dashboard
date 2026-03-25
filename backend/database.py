import json
import os
import sqlite3
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = Path(f"{BASE_DIR}/../database/schema.json")


def get_db_connection():
    connection = sqlite3.connect("database/ai_ops_database.db")
    connection.row_factory = sqlite3.Row
    return connection


def db_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema = {"tables": []}

    for t in tables:
        table_name = t["name"]
        if table_name.startswith("sqlite_"):
            continue

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        schema["tables"].append(
            {
                "name": table_name,
                "columns": [
                    {"name": col["name"], "type": col["type"]} for col in columns
                ],
            }
        )

    conn.close()

    SCHEMA_FILE.write_text(json.dumps(schema, indent=2))

    return schema
