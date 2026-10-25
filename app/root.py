from dataclasses import dataclass
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
)

# ports
from app.application.ports.repositories.file_storage_repository import (
    AbstractFileStorageRepository,
)
from app.application.ports.rag.vector_store import AbstractVectorStore
from app.application.ports.unit_of_work import AbstractUnitOfWork
from app.application.ports.rag.splitter import AbstractTextSplitter
from app.application.ports.rag.loader import AbstractDocumentLoader
from app.application.ports.rag.llm_client import AsyncLLMClient, RetryConfig

# working classes
from app.application.doc_processor import DocumentProcessor
from app.application.workflow import LangGraphWorkflow
from app.application.security import (
    PassLibPasswordHasher,
    HashLibHashService,
    JWTTokenService,
)
from app.application.vector_store_service import VectorStoreService
from app.infrastructure.rag.vector_store.faiss_vector_store import (
    FaissRetrieverFilter,
    FaissStore,
)
from app.core.config import settings
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.application.auth_service import AuthService
from app.application.file_ingestion_service import FileIngestionService
from app.application.chat_service import ChatService
from app.infrastructure.db import create_session_factory, create_db_engine, init_db
from app.infrastructure.rag.splitter import RecursiveCharacterSplitter
from app.infrastructure.rag.loaders import PDFLoader
from app.infrastructure.file_storage_repository import LocalFileStorageRepository
from app.infrastructure.rag.llm_client import OpenRouterLLMClient


@dataclass
class Container:
    db_engine: AsyncEngine
    document_processor: DocumentProcessor
    file_storage_repository: AbstractFileStorageRepository
    rag_workflow: LangGraphWorkflow
    password_hasher: PassLibPasswordHasher
    token_service: JWTTokenService
    hash_service: HashLibHashService
    session_maker: async_sessionmaker[AsyncSession]
    vector_store: AbstractVectorStore
    vector_store_service: VectorStoreService

    def get_uow(self) -> AbstractUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_maker)

    def get_vector_store(self) -> AbstractVectorStore:
        return self.vector_store

    def get_auth_service(self, uow: AbstractUnitOfWork) -> AuthService:
        return AuthService(
            uow, self.hash_service, self.token_service, self.password_hasher
        )

    def get_vector_store_service(self) -> VectorStoreService:
        return self.vector_store_service

    def get_file_ingestion_service(
        self, uow: AbstractUnitOfWork
    ) -> FileIngestionService:
        return FileIngestionService(
            uow,
            self.file_storage_repository,
            self.document_processor,
            self.vector_store_service,
            settings.FILE_UPLOAD_PATH,
        )

    def get_chat_service(self, uow: AbstractUnitOfWork) -> ChatService:
        return ChatService(uow, self.vector_store, self.rag_workflow)

    async def shutdown(self) -> None:
        # later we can also close the vector store connections also
        await self.db_engine.dispose()

    @classmethod
    async def create(cls):
        db_engine = create_db_engine(settings.DATABASE_URL)
        await init_db(db_engine)
        create_required_dir()
        vector_store = get_vector_store()
        return cls(
            db_engine=db_engine,
            document_processor=get_document_processor(),
            file_storage_repository=get_file_storage_repository(),
            rag_workflow=get_rag_workflow(),
            password_hasher=get_password_hasher(),
            token_service=get_token_service(),
            hash_service=get_hash_service(),
            session_maker=create_session_factory(db_engine),
            vector_store=vector_store,
            vector_store_service=VectorStoreService(vector_store),
        )


def get_faiss_retriever_filter() -> FaissRetrieverFilter:
    return FaissRetrieverFilter(
        search_type=settings.RETRIEVER_SEARCH_TYPE,
        top_k=settings.RETRIEVER_TOP_K_DOCS,
        fetch_k=settings.RETRIEVER_FAISS_PRE_DOC,
    )


def create_required_dir():
    for path in [
        settings.FILE_UPLOAD_PATH,
        settings.VECTOR_FOLDER,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def get_splitter() -> AbstractTextSplitter:
    return RecursiveCharacterSplitter(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)


def get_loaders() -> dict[str, AbstractDocumentLoader]:
    return {PDFLoader.supported_extension: PDFLoader()}


def get_document_processor()->DocumentProcessor:
    return DocumentProcessor(
        get_loaders(),
        get_splitter(),
    )


def get_embedding_model()->BaseChatModel:
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBED_MODEL,
        output_dimensionality=settings.EMBED_MODEL_SIZE,
        api_key=settings.GOOGLE_API_KEY,
    )


def get_file_storage_repository() -> AbstractFileStorageRepository:
    return LocalFileStorageRepository(settings.FILE_READ_CHUNK_SIZE)


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


def get_retry_config():
    return RetryConfig(
        max_attempts=settings.MAX_LLM_CALL_RETRIES,
        timeout=settings.LLM_CALL_ASYNC_TIMEOUT,
    )


def get_llm_client() -> AsyncLLMClient:
    return OpenRouterLLMClient(
        get_retry_config(),
        get_llm_model(),
    )


def get_rag_workflow() -> LangGraphWorkflow:
    return LangGraphWorkflow(get_llm_client())


def get_password_hasher() -> PassLibPasswordHasher:
    return PassLibPasswordHasher(settings.HASHING_ALGO)


def get_token_service() -> JWTTokenService:
    return JWTTokenService(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        settings.REFRESH_TOKEN_EXPIRE_DAYS,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )


def get_hash_service() -> HashLibHashService:
    return HashLibHashService()


def get_vector_store() -> AbstractVectorStore:
    return FaissStore.create_or_load(
        vector_dir=settings.VECTOR_FOLDER,
        embedding_client=get_embedding_model(),
        dimensions=settings.EMBED_MODEL_SIZE,
        retreiver_filter=get_faiss_retriever_filter()
    )
