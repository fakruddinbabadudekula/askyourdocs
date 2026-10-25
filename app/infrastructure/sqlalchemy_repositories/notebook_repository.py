from app.schemas.notebook import Notebook
from app.infrastructure.sqlalchemy_repositories.models.notebook import (
    Notebook as OrmNotebook,
)
from app.application.ports.repositories.notebook_repository import (
    AbstractNotebookRepository,
)
from app.infrastructure.sqlalchemy_repositories.mappers import (
    notebook_to_orm,
    orm_to_notebook,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from uuid import UUID


class NotebookRepository(AbstractNotebookRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, notebook: Notebook) -> None:
        self._db.add(notebook_to_orm(notebook))

    async def update(self, notebook: Notebook) -> None:
        await self._db.execute(
            update(OrmNotebook)
            .where(OrmNotebook.notebook_id == notebook.notebook_id)
            .values(title=notebook.title)
        )

    async def get_notebook(self, notebook_id: UUID) -> Notebook | None:
        result = await self._db.execute(
            select(OrmNotebook).where(OrmNotebook.notebook_id == notebook_id)
        )
        notebook_orm = result.scalar_one_or_none()
        return orm_to_notebook(notebook_orm) if notebook_orm else None

    async def get_notebooks(self, user_id: UUID) -> list[Notebook]:
        result = await self._db.execute(
            select(OrmNotebook).where(OrmNotebook.user_id == user_id)
        )
        notebooks_orm = result.scalars().all()
        return [orm_to_notebook(notebook) for notebook in notebooks_orm]

    async def delete_notebook(self, notebook_id: UUID) -> None:
        await self._db.execute(
            delete(OrmNotebook).where(OrmNotebook.notebook_id == notebook_id)
        )
