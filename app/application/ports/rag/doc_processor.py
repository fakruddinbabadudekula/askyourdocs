from abc import ABC, abstractmethod
from pathlib import Path
from langchain_core.documents.base import Document


class AbstractDocumentLoader(ABC):
    """Loads a raw file into SourceDocument(s)."""

    @abstractmethod
    async def load(self, file_path: Path) -> list[Document]: ...

    @property
    @abstractmethod
    def supported_extension(self) -> set[str]: ...


class AbstractTextSplitter(ABC):
    """Splits a SourceDocument into Chunks."""

    @abstractmethod
    def split(self, doc: list[Document]) -> list[Document]: ...


class DocumentProcesser(ABC):
    loaders: dict[str, AbstractDocumentLoader]
    splitter: AbstractTextSplitter

    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]: ...

    @abstractmethod
    async def load_and_split(self, file_path: Path) -> list[Document]: ...
