from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings


# This class wraps LangChains interface for embedding models
class LazyEmbedder(Embeddings):
    _model = None

    def _load(self):
        if self._model is None:
            self._model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return self._model

    def embed_documents(self, texts):
        if self._model is None:
            self._model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return self._model.embed_documents(texts)

    def embed_query(self, text):
        if self._model is None:
            self._model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return self._model.embed_query(text)


embedder = LazyEmbedder()

# Vector database configuration
vector_store = Chroma(
    collection_name="shared_vector_memory_bucket",
    embedding_function=embedder,
    persist_directory="./shared_rag_db",
)
