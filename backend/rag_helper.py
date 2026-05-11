from backend.rag_pipeline import RAGPipeline

rag = RAGPipeline()


# Helper function to start rag request and modify results
def rag_agent_resources(query: str, session_id: str = "supervisor-rag"):
    try:
        result = rag.query(query, session_id=session_id)
        return {"answer": result["answer"], "sources": result["context"]}

    except Exception as e:
        return {"answer": f"RAG error: {e}", "sources": []}
