from fastapi import APIRouter
from pydantic import BaseModel
from backend.rag_pipeline import RAGPipeline
from backend.conversation_memory import clear_session
from backend.document_memory import reload_documents

router = APIRouter(prefix="/rag", tags=["RAG"])
rag = RAGPipeline()


class RAGRequest(BaseModel):
    query: str
    session_id: str


@router.post("/query")
def rag_query(body: RAGRequest):
    return rag.query(body.query, body.session_id)


@router.post("/clear")
def clear_memory(session_id: str):
    clear_session(session_id)
    return {"status": "cleared"}


@router.post("/reload")
def rag_reload():
    return reload_documents("./docs")


@router.get("/test")
def rag_test():
    session_id = "test_session"
    test_query = "What information is stored in the shared vector memory?"
    result = rag.query(test_query, session_id=session_id)
    return {
        "message": "RAG pipeline test successful",
        "query": test_query,
        "answer": result["answer"],
        "context_used": result["context"],
        "history_used": result["history_used"],
    }
