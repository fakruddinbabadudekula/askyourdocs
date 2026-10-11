from uuid import UUID

from app.domain.entities.RetrieverFilter import RetrieverFilter
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
from app.infrastructure.file_repository import FileStorageRepository
from app.domain.repositories.file_repository import AbstractFileStorageRepository
from app.application.file_ingestion_service import FileIngestionService
from app.domain.unit_of_work import AbstractUnitOfWork
from app.application.vector_store_service import VectorStoreService
from app.application.auth_service import AuthService
from app.application.notebook_chat_service import NotebookChatService
from langchain_google_genai import ChatGoogleGenerativeAI


def get_loader() -> AbstractDocumentLoader:
    return PDFLoader()


def get_splitter() -> AbstractTextSplitter:
    return RecursiveCharacterSplitter(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)


def get_doc_loader() -> DocumentLoader:
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


def get_vector_store() -> AbstractVectorStore:
    if (settings.VECTOR_FOLDER / "index.faiss").exists():
        return FaissStore.load(
            vector_dir=settings.VECTOR_FOLDER, embedding_client=get_embedding_model()
        )

    return FaissStore.create(
        vector_dir=settings.VECTOR_FOLDER,
        embedding_client=get_embedding_model(),
        dimensions=settings.EMBED_MODEL_SIZE,
    )


def get_file_storage_repository() -> AbstractFileStorageRepository:
    return FileStorageRepository()


def get_vector_store_service(vector_store: AbstractVectorStore) -> VectorStoreService:
    return VectorStoreService(vector_store=vector_store)


def get_file_ingestion_service(
    uow: AbstractUnitOfWork, vector_service: VectorStoreService
) -> FileIngestionService:
    return FileIngestionService(
        uow=uow,
        file_storage=get_file_storage_repository(),
        doc_loader=get_doc_loader(),
        vector_service=vector_service,
        root_dir=settings.FILE_UPLOAD_PATH,
    )


def get_auth_service(uow: AbstractUnitOfWork) -> AuthService:
    return AuthService(uow=uow)


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
    # return ChatGoogleGenerativeAI(
    #     model="gemini-3.8-flash",
    #     api_key=settings.GOOGLE_API_KEY,
    #     temperature=0.7,
    #     max_retries=0,
    #     streaming=True,
    #     timeout=settings.CHAT_MODEL_TIMEOUT,
    # )


def get_llm_client() -> AsyncLLMClient:
    return LLMClient(
        get_llm_model(),
        RetryConfig(
            max_llm_call_retries=settings.MAX_LLM_CALL_RETRIES,
            llm_call_asyn_timeout=settings.LLM_CALL_ASYNC_TIMEOUT,
            retryable_llm_exceptions=settings.RETRYABLE_LLM_EXCEPTIONS,
        ),
    )


def get_retryable_llm_exceptions() -> set[BaseException]:
    return settings.RETRYABLE_LLM_EXCEPTIONS


def get_retriever_filter(user_id: UUID, notebook_id: UUID) -> RetrieverFilter:
    return RetrieverFilter.create(
        search_type=settings.RETRIEVER_SEARCH_TYPE,
        search_kwargs={
            "k": settings.RETRIEVER_TOP_K_DOCS,
            "fetch_k": settings.RETRIEVER_FAISS_PRE_DOC,
            "filter": {"user_id": str(user_id), "notebook_id": str(notebook_id)},
        },
    )


def get_rag_workflow() -> Workflow:
    return LangGraphWorkflow(get_llm_client())


def get_notebook_chat_service(
    uow: AbstractUnitOfWork, vector_store: AbstractVectorStore
) -> NotebookChatService:

    return NotebookChatService(
        uow=uow,
        vector_store=vector_store,
        workflow=get_rag_workflow(),
        retryable_exceptions=get_retryable_llm_exceptions(),
    )


def get_refresh_token_expire_days() -> int:
    return settings.REFRESH_TOKEN_EXPIRE_DAYS


def get_unit_of_work(session_maker) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session_maker)
