import os
from backend.lmstudio_llm import LMStudioLLM
from backend.shared_vector_memory import vector_store
from backend.conversation_memory import store_message, retrieve_history
from backend.conversation_memory import clear_session


class RAGPipeline:
    def __init__(self, persist_dir="./rag_db"):
        self.vector_store = vector_store
        self.llm = LMStudioLLM()

    def query(self, question, session_id: str, k=4):
        store_message(session_id, "user", question)

        history_docs = retrieve_history(session_id)
        history_text = "\n".join([d.page_content for d in history_docs])

        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(question)
        context = "\n\n".join([d.page_content for d in docs])

        prompt = (
            "Use ONLY the conversation history and context below to answer the question.\n"
            "If the answer is not in the context, say you don't know.\n\n"
            "Conversation history:\n" + history_text + "\n\n"
            "Context:\n" + context + "\n\n"
            "Question: " + question
        )

        answer = self.llm.invoke(prompt)
        store_message(session_id, "assistant", answer)

        results = {
            "answer": answer,
            "context": [
                {
                    "content": d.page_content,
                    "source": d.metadata.get("source", "unknown"),
                    "file": os.path.basename(d.metadata.get("source", "unknown")),
                }
                for d in docs
            ],
            "history_used": [d.page_content for d in history_docs],
        }

        clear_session(session_id)

        return results
