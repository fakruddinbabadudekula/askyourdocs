from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.notebook import Notebook

from enum import Enum


class NotebookSort(Enum):
    CREATED_AT_ASC = "created_at_asc"
    CREATED_AT_DESC = "created_at_desc"


class AbstractNotebookRepository(ABC):

    @abstractmethod
    async def save(self, notebook: Notebook) -> None: ...

    @abstractmethod
    async def update(self, notebook: Notebook) -> None: ...

    @abstractmethod
    async def get_notebook(self, notebook_id: UUID) -> Notebook | None: ...

    @abstractmethod
    async def get_notebooks(
        self, user_id: UUID, order_by: NotebookSort = NotebookSort.CREATED_AT_ASC
    ) -> list[Notebook]: ...

    @abstractmethod
    async def delete_notebook(self, notebook_id: UUID) -> None: ...
