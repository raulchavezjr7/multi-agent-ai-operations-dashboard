from fastapi import APIRouter, Request

from backend.agents.supervisor_agent import SupervisorAgent

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
async def chat_endpoint(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    supervisor = SupervisorAgent()
    supervisor_reply = supervisor.call_llm(prompt=user_message)

    return {"response": supervisor_reply}
