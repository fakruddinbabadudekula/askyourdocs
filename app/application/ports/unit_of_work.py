from abc import ABC, abstractmethod

from app.application.ports.repositories import (
    refresh_token_repository,
    user_repository,
    notebook_repository,
    files_metadata_repository,
    message_repository,
    document_ref_repository,
)


class AbstractUnitOfWork(ABC):
    users: user_repository.AbstractUserRepository
    refresh_tokens: refresh_token_repository.AbstractRefreshTokenRepository
    notebooks: notebook_repository.AbstractNotebookRepository
    files_metadata: files_metadata_repository.AbstractFilesMetadataRepository
    messages: message_repository.AbstractMessageRepository
    document_refs: document_ref_repository.AbstractDocumentRefRepository

    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abstractmethod
    async def __aexit__(self, *args) -> None:
        await self.rollback()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...
