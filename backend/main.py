from fastapi import FastAPI
from backend.routers import (
    accounting,
    agents,
    operations,
    inventory,
    sales,
    supervisor,
    support,
)

app = FastAPI(title="Ops Dashboard Backend API")

app.include_router(accounting.router)
app.include_router(agents.router)
app.include_router(inventory.router)
app.include_router(operations.router)
app.include_router(sales.router)
app.include_router(support.router)
app.include_router(supervisor.router)
