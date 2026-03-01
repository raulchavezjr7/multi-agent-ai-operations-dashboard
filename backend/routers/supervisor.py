from fastapi import APIRouter
from backend.agents.supervisor_agent import SupervisorAgent

router = APIRouter(prefix="/supervisor", tags=["Supervisor"])


@router.get("/task-test")
def task_test():
    supervisor = SupervisorAgent()
    supervisor.load_model(supervisor.model)

    outputs = []
    outputs.append(supervisor.call_llm("Give me a name of a AI OPS Dashboard"))
    outputs.append(
        supervisor.call_llm("Give me another name that is completely different")
    )
    outputs.append(supervisor.call_llm("combine them"))

    supervisor.end_task_mode()

    return {
        "message": "Supervisor agent task test",
        "results": outputs,
    }


@router.get("/test-rag")
def supervisor_rag_test():
    supervisor = SupervisorAgent()
    test_query = "Summarize the forklift safety rules."
    results = supervisor.call_llm_rag(test_query)

    return {"query": test_query, "supervisor_response": results}
