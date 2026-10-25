from abc import abstractmethod, ABC
from uuid import UUID
from app.schemas.user import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_user_by_email(self, user_email: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None: ...
