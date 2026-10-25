from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.document_ref import DocumentRef


class AbstractDocumentRefRepository(ABC):
    @abstractmethod
    async def save_bulk_doc_refs(self, doc_refs: list[DocumentRef]) -> None: ...

    @abstractmethod
    async def get_doc_refs(self, file_id: UUID) -> list[DocumentRef]: ...

    @abstractmethod
    async def delete_bulk_docs_by_file_id(self, file_id: UUID): ...

    @abstractmethod
    async def delete_by_doc_id(self, doc_id: UUID): ...

    @abstractmethod
    async def delete_bulk_docs_by_docs_id(self, doc_ids: list[UUID]) -> None: ...
