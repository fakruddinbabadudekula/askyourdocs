from abc import ABC, abstractmethod
from uuid import UUID
from app.schemas.document_ref import DocumentRef


class AbstractDocumentRefRepository(ABC):
    @abstractmethod
    async def save_bulk_doc_refs(self, chunks: list[DocumentRef]) -> None: ...

    @abstractmethod
    async def get_doc_refs(self, file_id: UUID) -> list[DocumentRef]: ...

    @abstractmethod
    async def delete_bulk_chunks_by_file_id(self, file_id: UUID): ...

    @abstractmethod
    async def delete_by_chunk(self, chunk_id: UUID): ...

    @abstractmethod
    async def delete_bulk_chunks_by_doc_id(self, doc_ids: list[UUID]) -> None: ...
