from app.application.ports.unit_of_work import AbstractUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.infrastructure.sqlalchemy_repositories import (
    user_repository,
    refresh_token_repository,
    notebook_repository,
    message_repository,
    files_metadata_repository,
    document_ref_repository,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker
        self.db_session: AsyncSession | None = None

    async def __aenter__(self):
        self.db_session = self.session_maker()
        self.users = user_repository.UserRepository(self.db_session)
        self.refresh_tokens = refresh_token_repository.RefreshTokenRepository(
            self.db_session
        )
        self.notebooks = notebook_repository.NotebookRepository(self.db_session)
        self.document_refs = document_ref_repository.DocumentRefRepository(
            self.db_session
        )
        self.messages = message_repository.MessageRepository(self.db_session)
        self.files_metadata = files_metadata_repository.FileMetadataRepository(
            self.db_session
        )
        return await super().__aenter__()

    async def commit(self) -> None:
        await self.db_session.commit()

    async def rollback(self) -> None:
        await self.db_session.rollback()

    async def __aexit__(self, *args) -> None:
        await super().__aexit__(*args)
        await self.db_session.close()

    async def flush(self):
        await self.db_session.flush()
