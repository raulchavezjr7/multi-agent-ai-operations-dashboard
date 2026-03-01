from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma


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

vector_store = Chroma(
    collection_name="shared_vector_memory_bucket",
    embedding_function=embedder,
    persist_directory="./shared_rag_db",
)
