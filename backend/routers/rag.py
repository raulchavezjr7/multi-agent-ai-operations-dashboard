import os
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.conversation_memory import clear_session
from backend.document_memory import reload_documents
from backend.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/rag", tags=["RAG"])
rag = RAGPipeline()

UPLOAD_BASE = "./docs"
TXT_DIR = os.path.join(UPLOAD_BASE, "txt")
PDF_DIR = os.path.join(UPLOAD_BASE, "pdf")
os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


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
    reload_documents("./docs")
    return {"status": "initialized"}


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    saved_files = []

    for file in files:
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".txt", ".pdf"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type for '{filename}'. Only .txt and .pdf are allowed.",
            )

        target_dir = TXT_DIR if ext == ".txt" else PDF_DIR
        target_path = os.path.join(target_dir, filename)

        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)

        saved_files.append(filename)

    return {"status": "ok", "saved_files": saved_files}


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
