from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.file_metadata import FileMetadata


class AbstractFilesMetadataRepository(ABC):

    @abstractmethod
    async def save(self, file_metadata: FileMetadata) -> None: ...

    @abstractmethod
    async def get_file_metadata(self, file_id: UUID) -> FileMetadata | None: ...

    @abstractmethod
    async def get_files_metadata(
        self, notebook_id: UUID
    ) -> list[FileMetadata | None]: ...

    @abstractmethod
    async def delete_file_metadata(self, file_id: UUID) -> None: ...
