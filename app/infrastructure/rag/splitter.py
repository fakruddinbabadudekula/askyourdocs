from app.application.ports.rag.splitter import AbstractTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RecursiveCharacterSplitter(AbstractTextSplitter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size < 100:
            raise ValueError(f"chunk_size too small: {chunk_size} (min 100)")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split(self, doc):
        return self._splitter.split_documents(doc)