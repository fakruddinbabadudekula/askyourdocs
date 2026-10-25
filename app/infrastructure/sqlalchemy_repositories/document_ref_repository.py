
from app.application.ports.repositories.document_ref_repository import (
    AbstractDocumentRefRepository,
)
from app.infrastructure.sqlalchemy_repositories.models.document_ref import (
    DocumentRef as OrmDocumentRef,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.infrastructure.sqlalchemy_repositories.mappers import (
    document_ref_to_orm,
    orm_to_document_ref,
)


class DocumentRefRepository(AbstractDocumentRefRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save_bulk_doc_refs(self, doc_refs):
        refs_orm = [document_ref_to_orm(ref) for ref in doc_refs]
        self._db.add_all(refs_orm)

    async def get_doc_refs(self, file_id):
        result = await self._db.execute(
            select(OrmDocumentRef).where(OrmDocumentRef.file_id == file_id)
        )
        refs_orm = result.scalars().all()
        return [orm_to_document_ref(ref) for ref in refs_orm]

    async def delete_bulk_docs_by_file_id(self, file_id):
        await self._db.execute(
            delete(OrmDocumentRef).where(OrmDocumentRef.file_id == file_id)
        )

    async def delete_by_doc_id(self, doc_id):
        await self._db.execute(
            delete(OrmDocumentRef).where(OrmDocumentRef.doc_id == doc_id)
        )

    async def delete_bulk_docs_by_docs_id(self, doc_ids):
        await self._db.execute(
            delete(OrmDocumentRef).where(OrmDocumentRef.doc_id.in_(doc_ids))
        )
