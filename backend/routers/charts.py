import json
import re

from fastapi import APIRouter, Request

from backend.charts_nosql_helper import (
    add_chart,
    delete_chart,
    get_all_charts,
    get_chart,
    update_chart,
)

router = APIRouter(prefix="/charts", tags=["Charts"])


@router.get("/")
def read_charts():
    return get_all_charts()


@router.get("/{chart_id}")
def read_chart(chart_id: str):
    return get_chart(chart_id)


@router.post("/")
async def create_chart(request: Request):
    body = await request.json()
    json_match = re.search(r"\{[\s\S]*\}", body["test"])

    if json_match:
        json_str = json_match.group(0)
        cleaned_body = (
            json_str.replace("```", "").replace(r"\n", "").replace(r"\"", '"')
        )
        json_body = json.loads(cleaned_body)
        return add_chart(json_body)
    return {"error": "Incorrect Format"}


@router.put("/{chart_id}")
async def modify_chart(chart_id: str, request: Request):
    body = await request.json()
    return update_chart(chart_id, body)


@router.delete("/{chart_id}")
async def remove_chart(chart_id: str):
    return delete_chart(chart_id)
