import os

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFDirectoryLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.shared_vector_memory import vector_store


# These functions help load new files into vector memory
def load_documents(folder: str = "./docs"):
    txt_loader = DirectoryLoader(
        f"{folder}/txt",
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    txt_docs = txt_loader.load()

    pdf_loader = PyPDFDirectoryLoader(f"{folder}/pdf")
    pdf_docs = pdf_loader.load()

    docs = txt_docs + pdf_docs

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["type"] = "document"
        chunk.metadata["file_name"] = os.path.basename(
            chunk.metadata.get("source", "unknown")
        )

    vector_store.add_documents(chunks)


def clear_documents():
    vector_store._collection.delete(where={"type": "document"})


def reload_documents(folder: str = "./docs"):
    clear_documents()
    return load_documents(folder)
