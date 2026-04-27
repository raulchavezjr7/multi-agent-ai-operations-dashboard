from fastapi import APIRouter

from backend.overview_nosql_helper import get_all_overview

router = APIRouter(prefix="/overview", tags=["Overview"])


@router.get("/all")
def read_all_overview():
    return get_all_overview()
