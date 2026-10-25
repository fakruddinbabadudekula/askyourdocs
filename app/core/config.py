"""Centralized config file"""

from pydantic_settings import (
    BaseSettings,
)  # Automatically reads environment variables and Validates the data

from functools import (
    lru_cache,
)

from pathlib import Path


class Settings(BaseSettings):

    # API keys....
    OPENROUTER_BASE_URL: str
    OPENROUTER_API_KEY: str
    GOOGLE_API_KEY: str

    # Model Config
    CURRENT_CHAT_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    TEMPERATURE: float = 0.7

    # Base File Path
    BASE_PATH: Path = Path(__file__).resolve().parents[2]

    # App Information
    APP_NAME: str = "NotebookLm"
    APP_PATH: Path = BASE_PATH / "app"

    # Data Path
    DATA_PATH: Path = BASE_PATH / "data"

    # Vector
    VECTOR_FOLDER: Path = DATA_PATH / "vectors"

    # Data Path where uploaded files are stored
    FILE_UPLOAD_PATH: Path = DATA_PATH / "upload_files"

    # File Read chunk size of upload file
    FILE_READ_CHUNK_SIZE: int = 1024 * 1024  # 1MB

    # Embedding Model
    EMBED_MODEL: str = "gemini-embedding-001"
    EMBED_MODEL_SIZE: int = 768

    # DataBase
    DATABASE_URL: str

    # Password Hashing
    HASHING_ALGO: str = "argon2"

    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    SECRET_KEY: str
    ALGORITHM: str

    # Timeouts
    CHAT_MODEL_TIMEOUT: int = 30
    LLM_CALL_ASYNC_TIMEOUT: int = 40

    # Retries
    MAX_LLM_CALL_RETRIES: int = 3
    MAX_PDF_PROCESS_RETRY: int = 3

    # Vector Store
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    RETRIEVER_SEARCH_TYPE: str = "similarity"
    RETRIEVER_TOP_K_DOCS: int = 5
    RETRIEVER_FAISS_PRE_DOC: int = 100

    # Cookie
    COOKIE_SECURE: bool = False

    class Config:
        env_file = ".env"  # Look for .env file
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
