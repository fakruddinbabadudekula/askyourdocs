from typing import AsyncIterator
from pathlib import Path
from app.domain.repositories.file_repository import AbstractFileStorageRepository
from app.domain.unit_of_work import AbstractUnitOfWork
from uuid import UUID
from app.core.exceptions import InvalidCredentialsException,InvalidFilePaths, UnSupportedResource
from app.domain.Notebook import Notebook, FileMetadata
from app.rag.interface.doc_loader import DocumentLoader
from app.application.vector_store_service import VectorStoreService
from app.domain.Chunk import Chunk


class FileIngestionService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        file_storage: AbstractFileStorageRepository,
        doc_loader: DocumentLoader,
        vector_service: VectorStoreService,
        root_dir: Path,
    ):
        self._uow = uow
        self._file_storage = file_storage
        self._root_dir = root_dir
        self._doc_loader = doc_loader
        self._vector_service = vector_service

    def validate_file(self, file_ext: str) -> None:
        if file_ext not in self._doc_loader.supported_extensions:
            raise UnSupportedResource(
                "Unsupported_file_ext",
                details={"ext": file_ext},
            )

    def get_file_distination(
        self,
        notebook_id: UUID | str,
        user_id: UUID | str,
        file_name: str,
        file_ext: str,
    ):
        destination = Path(
            f"{self._root_dir / str(user_id) / str(notebook_id) / file_name}"
        ).resolve()
        if not destination.is_relative_to(self._root_dir):
            raise InvalidFilePaths(
                "invalid file path",
                details={
                    "user_id": str(user_id),
                    "session_id": str(notebook_id),
                    "file_name": str(file_name),
                    "file_ext": str(file_ext),
                },
            )

        return destination

    async def upload_files(
        self,
        stream: AsyncIterator[bytes],
        file_name: str,
        file_ext: str,
        notebook_id: UUID | None,
        user_id: UUID,
    ) -> FileMetadata:
        self.validate_file(file_ext)
        async with self._uow:
            if notebook_id:
                notebook = await self._uow.notebooks.get_notebook(notebook_id)
                if notebook is None:
                    raise InvalidCredentialsException(
                        "Invalid Notebook Id",
                        details={
                            "user_id": str(user_id),
                            "notebook_id": str(notebook_id),
                        },
                    )
            else:
                notebook = Notebook.create(user_id)
                await self._uow.notebooks.create_notebook(notebook)
            file_destination = self.get_file_distination(
                notebook.notebook_id, notebook.user_id, file_name, file_ext
            )
            file_size = await self._file_storage.save(
                stream,
                file_destination,
            )
            file_metadata = notebook.add_file_metadata(
                type=file_ext, name=file_name, size=file_size
            )
            metadata = {
                "user_id": str(user_id),
                "notebook_id": str(file_metadata.notebook_id),
                "file_name": str(file_metadata.name),
                "file_ext": str(file_metadata.type),
                "file_id": str(file_metadata.file_id),
            }
            docs = await self._doc_loader.load_and_split(file_destination)
            doc_ids = await self._vector_service.aadd_documents_with_metadata(
                docs, metadata
            )

            chunks = [
                Chunk(chunk_id=chunk_id, file_id=file_metadata.file_id)
                for chunk_id in doc_ids
            ]
            await self._uow.notebooks.save(notebook)
            await self._uow.flush()  # we need to flush here to create files_metadata instance in db, bcz chunk table have foriegn key file_id.
            await self._uow.chunks.create_bulk_chunks(chunks)
            notebook.clear_changes()
            await self._uow.commit()
            return file_metadata
