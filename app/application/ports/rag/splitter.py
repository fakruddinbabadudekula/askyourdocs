from abc import ABC, abstractmethod
from pathlib import Path
from langchain_core.documents.base import Document


class AbstractTextSplitter(ABC):
    """Splits a SourceDocument into Chunks."""

    @abstractmethod
    def split(self, doc: list[Document]) -> list[Document]: ...
