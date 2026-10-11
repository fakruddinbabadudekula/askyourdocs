from dataclasses import dataclass
from uuid import UUID
from app.domain.entities.RetrieverFilter import RetrieverFilter
from app.domain.security import HashService, PasswordHasher, TokenService
from app.infrastructure.security import (
    HashLibHashService,
    JWTTokenService,
    PassLibPasswordHasher,
)
from app.infrastructure.db import create_db_engine, create_session_factory, init_db
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.rag.interface.workflow import Workflow
from app.infrastructure.rag.workflow import LangGraphWorkflow
from app.rag.interface.doc_process import (
    AbstractDocumentLoader,
    AbstractTextSplitter,
)
from app.rag.interface.llm_client import AsyncLLMClient
from app.infrastructure.rag.llm_clients import LLMClient, RetryConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from app.infrastructure.rag.loaders import PDFLoader
from app.infrastructure.rag.splitters import RecursiveCharacterSplitter
from app.infrastructure.rag.doc_loader import LangchainDocumentLoader
from app.rag.interface.doc_loader import DocumentLoader
from app.core.config import settings
from app.rag.interface.vector_store import AbstractVectorStore
from app.infrastructure.rag.vector_stores.faiss_store import FaissStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings
from app.infrastructure.file_repository import FileStorageRepository
from app.domain.repositories.file_repository import AbstractFileStorageRepository
from app.application.file_ingestion_service import FileIngestionService
from app.domain.unit_of_work import AbstractUnitOfWork
from app.application.vector_store_service import VectorStoreService
from app.application.auth_service import AuthService
from app.application.notebook_chat_service import NotebookChatService
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from openai import (
    APIError,
    RateLimitError,
)
import asyncio


@dataclass
class Container:
    pdf_loader: AbstractDocumentLoader
    text_splitter: AbstractTextSplitter
    document_loader: DocumentLoader
    embedding_model: Embeddings
    file_storage_repository: AbstractFileStorageRepository
    llm_client: AsyncLLMClient
    rag_workflow: Workflow
    llm_model: BaseChatModel
    password_hasher: PasswordHasher
    token_service: TokenService
    hash_service: HashService
    session_maker: async_sessionmaker[AsyncSession]
    vector_store: AbstractVectorStore | None
    retryable_llm_exceptions: tuple[type[BaseException], ...]

    def get_uow(self) -> AbstractUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_maker)

    def get_vector_store(self) -> AbstractVectorStore:
        return FaissStore.create_or_load(
            self.vector_folder, self.embedding_model, self.embedding_dimenstions
        )

    def get_auth_service(self, uow: AbstractUnitOfWork) -> AuthService:
        return AuthService(
            uow, self.hash_service, self.token_service, self.password_hasher
        )

    def get_vector_store_service(self) -> VectorStoreService:
        return VectorStoreService(self.vector_store)

    def get_file_ingestion_service(
        self, uow: AbstractUnitOfWork
    ) -> FileIngestionService:
        return FileIngestionService(
            uow,
            self.file_storage_repository,
            self.document_loader,
            self.get_vector_store_service(),
            settings.FILE_UPLOAD_PATH,
        )

    def get_notebook_chat_service(self, uow: AbstractUnitOfWork) -> NotebookChatService:
        return NotebookChatService(
            uow, self.vector_store, self.rag_workflow, self.retryable_llm_exceptions
        )

    def get_retriever_filter(self, user_id: UUID, notebook_id: UUID) -> RetrieverFilter:
        return RetrieverFilter.create(
            search_type=settings.RETRIEVER_SEARCH_TYPE,
            search_kwargs={
                "k": settings.RETRIEVER_TOP_K_DOCS,
                "fetch_k": settings.RETRIEVER_FAISS_PRE_DOC,
                "filter": {"user_id": str(user_id), "notebook_id": str(notebook_id)},
            },
        )

    @classmethod
    async def get_container(cls):
        db_engine = create_db_engine(settings.DATABASE_URL)
        await init_db(db_engine)
        create_required_dir()
        return cls(
            pdf_loader=PDFLoader(),
            text_splitter=get_splitter(),
            document_loader=get_document_loader(),
            embedding_model=get_embedding_model(),
            file_storage_repository=get_file_storage_repository(),
            llm_client=get_llm_model(),
            rag_workflow=get_rag_workflow(),
            llm_model=get_llm_model(),
            password_hasher=get_password_hasher(),
            token_service=get_token_service(),
            hash_service=get_hash_service(),
            retryable_llm_exceptions=get_retryable_llm_exceptions(),
            vector_store=get_vector_store(),
            session_maker=create_session_factory(db_engine),
        )


def create_required_dir():
    for path in [
        settings.FILE_UPLOAD_PATH,
        settings.VECTOR_FOLDER,
    ]:
        path.mkdir(parents=True, exist_ok=True)
        
def get_loader() -> AbstractDocumentLoader:
    return PDFLoader()


def get_splitter() -> AbstractTextSplitter:
    return RecursiveCharacterSplitter(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)


def get_document_loader():
    return LangchainDocumentLoader(
        {
            ".pdf": get_loader(),
        },
        get_splitter(),
    )


def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBED_MODEL,
        output_dimensionality=settings.EMBED_MODEL_SIZE,
        api_key=settings.GOOGLE_API_KEY,
    )


def get_file_storage_repository() -> AbstractFileStorageRepository:
    return FileStorageRepository()


def get_llm_model() -> BaseChatModel:
    return ChatOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        model=settings.CURRENT_CHAT_MODEL,
        temperature=settings.TEMPERATURE,
        streaming=True,
        timeout=settings.CHAT_MODEL_TIMEOUT,
        max_retries=0,
    )


def get_llm_client() -> AsyncLLMClient:
    return LLMClient(
        get_llm_model(),
        RetryConfig(
            max_llm_call_retries=settings.MAX_LLM_CALL_RETRIES,
            llm_call_asyn_timeout=settings.LLM_CALL_ASYNC_TIMEOUT,
            retryable_llm_exceptions=get_retryable_llm_exceptions(),
        ),
    )


def get_rag_workflow() -> Workflow:
    return LangGraphWorkflow(get_llm_client())


def get_password_hasher() -> PasswordHasher:
    return PassLibPasswordHasher(settings.HASHING_ALGO)


def get_token_service() -> TokenService:
    return JWTTokenService(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        settings.REFRESH_TOKEN_EXPIRE_DAYS,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )


def get_hash_service() -> HashService:
    return HashLibHashService()


def get_retryable_llm_exceptions() -> tuple[type[BaseException], ...]:
    return (
        ConnectionError,
        asyncio.TimeoutError,
        RateLimitError,
        APIError,
    )  # type[BaseException] means classess of BaseException instead of instance


def get_vector_store() -> AbstractVectorStore:

    return FaissStore.create_or_load(
        vector_dir=settings.VECTOR_FOLDER,
        embedding_client=get_embedding_model(),
        dimensions=settings.EMBED_MODEL_SIZE,
    )


