from typing import Any
from app.application.ports.rag.vector_store import AbstractVectorStore
from langchain_core.documents.base import Document
import time
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self, vector_store: AbstractVectorStore):
        self._vector_store = vector_store

    def _add_additional_metadata_to_doc(
        self, docs: list[Document], metadata: dict
    ) -> Document:
        for doc in docs:
            doc.metadata.update(metadata)
        return docs

    async def aadd_documents_with_metadata(
        self, docs: list[Document], metadata: dict[str, Any] | None
    ) -> list[str]:
        start = time.perf_counter()
        if len(docs) == 0 or not docs:
            raise ValueError(f"Docs must be atleast one. Passed empty")

        docs_ids = await self._vector_store.add_documents(
            self._add_additional_metadata_to_doc(docs, metadata)
        )
        logger.info(
            "Successfully_added_docs_to_vector_store",
            extra={
                "count": len(docs),
                "duration": time.perf_counter() - start,
            },
        )
        return docs_ids

    async def adelete_documents(self, doc_ids: list[str]) -> None | bool:
        start = time.perf_counter()
        result = await self._vector_store.delete(doc_ids)
        if result or result is None:
            logger.info(
                "Succesfully_deleted_docs_from_vector_store",
                extra={"count": len(doc_ids), "duration": time.perf_counter() - start},
            )
        else:
            logger.info("Unable_to_delete_docs", extra={"docs_ids": doc_ids})
        return result
