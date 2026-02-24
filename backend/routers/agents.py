from fastapi import APIRouter
from backend.agents.supervisor_agent import SupervisorAgent

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/overview")
def agent_summary():
    supervisor = SupervisorAgent()
    results = supervisor.run_all()
    return {
        "message": "Supervisor agent overview from all agent data",
        "results": results,
    }
