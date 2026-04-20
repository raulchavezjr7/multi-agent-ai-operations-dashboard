from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    accounting,
    charts,
    chat,
    inventory,
    operations,
    overview,
    rag,
    sales,
    sql,
    supervisor,
    support,
)

app = FastAPI(title="Ops Dashboard Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounting.router)
app.include_router(chat.router)
app.include_router(charts.router)
app.include_router(inventory.router)
app.include_router(operations.router)
app.include_router(overview.router)
app.include_router(rag.router)
app.include_router(sales.router)
app.include_router(sql.router)
app.include_router(support.router)
app.include_router(supervisor.router)
