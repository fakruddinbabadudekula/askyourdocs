from abc import ABC, abstractmethod
from typing import Any
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_core.documents.base import Document


class AbstractVectorStore(ABC):
    @abstractmethod
    async def add_documents(
        self,
        chunks: list[Document],
    ) -> list[str]: ...

    @abstractmethod
    async def delete(self, document_ids: list[str]) -> None | bool: ...

    @abstractmethod
    def get_retriever(self, **kwargs: Any) -> VectorStoreRetriever: ...
