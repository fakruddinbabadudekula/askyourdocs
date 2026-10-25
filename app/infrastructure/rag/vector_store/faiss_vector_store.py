from pathlib import Path
from app.application.ports.rag.vector_store import AbstractVectorStore
import faiss
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents.base import Document
from dataclasses import dataclass


@dataclass
class FaissRetrieverFilter:
    search_type: str
    top_k: int
    fetch_k: int


class FaissStore(AbstractVectorStore):
    def __init__(
        self,
        vector_store: FAISS,
        vector_dir: Path,
        retreiver_filter: FaissRetrieverFilter,
    ):
        self._store = vector_store
        self._store_path = vector_dir
        self._retreiver_filter = retreiver_filter

    @classmethod
    def create_or_load(
        cls,
        vector_dir: Path,
        embedding_client: Embeddings,
        dimensions: int,
        retreiver_filter: FaissRetrieverFilter,
    ) -> "FaissStore":
        if (vector_dir / "index.faiss").exists():
            store = FAISS.load_local(
                str(vector_dir),
                embedding_client,
                allow_dangerous_deserialization=True,
            )
            return cls(store, vector_dir, retreiver_filter)
        if dimensions <= 0:
            raise ValueError(f"dimensions must be > 0, got {dimensions}")
        vector_dir.mkdir(parents=True, exist_ok=True)
        index = faiss.IndexFlatL2(dimensions)
        store = FAISS(
            embedding_function=embedding_client,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        store.save_local(str(vector_dir))
        return cls(store, vector_dir, retreiver_filter)

    async def add_documents(self, chunks):
        docs = [
            Document(page_content=chunk.page_content, metadata=chunk.metadata)
            for chunk in chunks
        ]
        ids = await self._store.aadd_documents(docs)
        self._store.save_local(str(self._store_path))
        return ids

    async def delete(self, chunk_ids):
        return self._store.adelete(chunk_ids)

    def get_retriever(self, **kwargs):
        search_type = self._retreiver_filter.search_type
        search_kwargs = {
            "k": self._retreiver_filter.top_k,
            "fetch_k": self._retreiver_filter.fetch_k,
            "filter": kwargs,
        }
        return self._store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )
