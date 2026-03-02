from datetime import datetime, timezone

from langchain_core.documents import Document

from backend.shared_vector_memory import vector_store


def store_message(session_id: str, role: str, content: str):
    doc = Document(
        page_content=content,
        metadata={
            "type": "conversation",
            "session_id": session_id,
            "role": role,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    vector_store.add_documents([doc])


def retrieve_history(session_id: str, k: int = 6):
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"$and": [{"type": "conversation"}, {"session_id": session_id}]},
        }
    )
    return retriever.invoke("conversation history")


def clear_session(session_id: str):
    vector_store._collection.delete(
        where={"$and": [{"type": "conversation"}, {"session_id": session_id}]}
    )
