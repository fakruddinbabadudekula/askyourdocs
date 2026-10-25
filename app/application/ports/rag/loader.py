from abc import ABC, abstractmethod
from pathlib import Path
from langchain_core.documents.base import Document


class AbstractDocumentLoader(ABC):
    """Loads a raw file into SourceDocument(s)."""

    supported_extension: str

    @abstractmethod
    async def load(self, file_path: Path) -> list[Document]: ...

