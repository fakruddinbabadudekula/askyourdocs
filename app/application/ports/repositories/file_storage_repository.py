from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator


class AbstractFileStorageRepository(ABC):
    @abstractmethod
    async def save(self, stream: AsyncIterator[bytes], destination: Path) -> int: ...

    @abstractmethod
    async def delete(self, file_path: Path) -> None: ...