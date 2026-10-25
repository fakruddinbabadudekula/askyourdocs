from app.application.ports.rag.loader import AbstractDocumentLoader
from app.application.ports.rag.splitter import AbstractTextSplitter
from pathlib import Path
import logging
import time

logger = logging.getLogger(__name__)


class DocumentProcessor:

    def __init__(
        self, loaders: dict[str, AbstractDocumentLoader], splitter: AbstractTextSplitter
    ):
        self._loaders = loaders
        self._splitter = splitter

    @property
    def supported_extensions(self):
        return set(self._loaders.keys())

    def _validate_and_return_ext(self, file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"file_not_found. path={file_path}")
        ext = file_path.suffix.lower()[1:]
        if ext not in self._loaders:
            raise ValueError(f"unsupported_file_type. ext={ext}")
        return ext

    async def load_and_split(
        self,
        file_path: Path,
    ):
        ext = self._validate_and_return_ext(file_path)
        loader = self._loaders[ext]
        t0 = time.perf_counter()
        docs = await loader.load(file_path)
        logger.info(
            "doc_loaded",
            extra={
                "file": file_path.name,
                "pages": len(docs),
                "duration": time.perf_counter() - t0,
            },
        )

        t1 = time.perf_counter()
        chunks = self._splitter.split(docs)
        logger.info(
            "doc_chunked",
            extra={
                "file": file_path.name,
                "chunks": len(chunks),
                "duration": time.perf_counter() - t1,
            },
        )

        return chunks
