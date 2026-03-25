import json

from fastapi import APIRouter
from pydantic import BaseModel

from backend.database import SCHEMA_FILE, db_schema, get_db_connection

router = APIRouter(prefix="/sql", tags=["SQL"])


class SQLQuery(BaseModel):
    query: str


@router.post("/")
def run_sql(query: SQLQuery):
    conn = get_db_connection()
    try:
        cursor = conn.execute(query.query)
        rows = cursor.fetchall()
        dict_rows = [dict(row) for row in rows]
        columns = list(dict_rows[0].keys()) if dict_rows else []
        list_rows = [list(row.values()) for row in dict_rows]

        return {"columns": columns, "rows": list_rows}

    except Exception as e:
        return {"error": str(e)}

    finally:
        conn.close()


@router.get("/generate-schema")
def generate_schema():
    db_schema()
    return {"message": "Schema extracted", "schema_file": str(SCHEMA_FILE)}


@router.get("/schema")
def get_schema():
    try:
        data = SCHEMA_FILE.read_text()
        return json.loads(data)
    except FileNotFoundError:
        return {"error": "Schema file not found. Run /sql/schema/generate first."}
