from fastapi import FastAPI
from app.core.logging import setup_logging
from logging import getLogger
from app.interface.api.cookie import CookiePolicy
from app.interface.api.exception_handlers import register_exception_handlers
from app.interface.api.routes.auth import router as auth_router
from app.interface.api.routes.register import router as register_router
from app.interface.api.routes.upload import router as upload_router
from app.interface.api.routes.chat import router as chat_router
from app.interface.api.routes.test import router as test_router
from app.interface.api.middleware import logger_middleware
from contextlib import asynccontextmanager
from app.root import Container
from app.core.config import settings



logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    setup_logging()
    logger.info("Server Started")
    app.state.container=await Container.get_container()
    app.state.cookie_policy=CookiePolicy(secure=settings.COOKIE_SECURE)
    logger.info("Tables are created ")
    yield
    logger.info("Server terminated")


tags_metadata = [
    {"name": "auth", "description": "Login, token refresh, and logout."},
    {
        "name": "test",
        "description": "test purpose only: have get_user which returns current user.",
    },
    {"name": "register", "description": "New user registration."},
    {
        "name": "upload",
        "description": "Upload PDF documents into a session's vector store.",
    },
    {
        "name": "chat",
        "description": "Ask questions and get RAG-powered, cited answers.",
    },
    {"name": "history", "description": "Browse past sessions and messages."},
    {"name": "health", "description": "For health checkup."},
]
app = FastAPI(
    title="Production RAG API",
    description="""
Backend for a document-grounded chat assistant. Upload PDFs into a session,
then ask questions — answers are generated from retrieved chunks of your
documents, with citations back to the source.

### Auth
Most endpoints require `Authorization: Bearer <access_token>`, obtained via
`/api/v1/auth/login`. Refresh tokens are stored in an `HttpOnly` cookie.
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)
app.middleware("http")(logger_middleware)
register_exception_handlers(app=app)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(register_router, prefix="/api/v1", tags=["register"])
app.include_router(upload_router, prefix="/api/v1", tags=["upload"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(test_router, prefix="/api/v1", tags=["test"])


@app.get("/")
def hello():
    return {"msg": "Hello user. How are you?"}


@app.get("/health", tags=["health"])
def health():
    return {"msg": "Yah, I am fine."}
