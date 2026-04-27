from fastapi import APIRouter, Request

from backend.agents.supervisor_agent import SupervisorAgent

router = APIRouter(prefix="/chat", tags=["Chat"])

supervisor = SupervisorAgent()
model_loaded = False


@router.post("/session/load")
async def load_chat_model():
    global model_loaded
    if not model_loaded:
        supervisor.load_model(supervisor.model)
        model_loaded = True
    return {"status": "loaded"}


@router.post("/session/unload")
async def unload_chat_model():
    global model_loaded
    if model_loaded:
        supervisor.unload_model(supervisor.model)
        supervisor.conversation = []
        model_loaded = False
    return {"status": "unloaded"}


# @router.post("/")
# async def chat_endpoint(request: Request):
#     body = await request.json()
#     user_message = body.get("message", "")

#     supervisor = SupervisorAgent()
#     supervisor_reply = supervisor.call_llm(prompt=user_message)

#     return {"response": supervisor_reply}


@router.post("/no-rag")
async def chat_no_rag(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    reply = supervisor.call_llm(prompt=user_message)
    return {"response": reply}


@router.post("/semi-rag")
async def chat_semi(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    reply = supervisor.call_llm_semi_rag(prompt=user_message)
    return {"response": reply}


@router.post("/full-rag")
async def chat_rag(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    reply = supervisor.call_llm_rag(prompt=user_message)
    return {"response": reply}
