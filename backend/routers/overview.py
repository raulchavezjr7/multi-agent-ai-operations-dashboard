from fastapi import APIRouter

from backend.overview_nosql_helper import get_all_overview

router = APIRouter()


@router.get("/overview/all")
def read_all_overview():
    return get_all_overview()
