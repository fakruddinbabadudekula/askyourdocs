from app.domain.file_metadata import FileMetadata
from app.application.ports.repositories.files_metadata_repository import (
    AbstractFilesMetadataRepository,
)
from app.infrastructure.sqlalchemy_repositories.models.file import (
    FileMetadata as OrmFileMetadata,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.infrastructure.sqlalchemy_repositories.mappers import (
    file_to_orm,
    orm_to_file,
)
from uuid import UUID


class FileMetadataRepository(AbstractFilesMetadataRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, file_metadata: FileMetadata) -> None:
        self._db.add(file_to_orm(file_metadata))

    async def get_file_metadata(self, file_id: UUID) -> FileMetadata | None:
        result = await self._db.execute(
            select(OrmFileMetadata).where(OrmFileMetadata.file_id == file_id)
        )
        file_orm = result.scalar_one_or_none()
        return orm_to_file(file_orm) if file_orm else None

    async def get_files_metadata(self, notebook_id: UUID) -> list[FileMetadata | None]:
        result = await self._db.execute(
            select(OrmFileMetadata).where(OrmFileMetadata.notebook_id == notebook_id)
        )
        files_orm = result.scalars().all()
        return [orm_to_file(file) for file in files_orm]

    async def delete_file_metadata(self, file_id: UUID) -> None:
        await self._db.execute(
            delete(OrmFileMetadata).where(OrmFileMetadata.file_id == file_id)
        )
