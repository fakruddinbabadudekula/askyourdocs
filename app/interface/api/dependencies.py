from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError
from app.application.notebook_chat_service import NotebookChatService
from app.core.exceptions import InvalidCredentialsException
from app.domain.unit_of_work import AbstractUnitOfWork
from app.application.file_ingestion_service import FileIngestionService
from app.application.auth_service import AuthService
from uuid import UUID
from app.root import Container

security = HTTPBearer()


def get_container(request: Request) -> Container:
    return request.app.state.container



def get_uow(container: Container = Depends(get_container)) -> AbstractUnitOfWork:
    return container.get_uow()


def get_auth_service(
    container: Container = Depends(get_container),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> AuthService:
    return container.get_auth_service(uow)


def get_notebook_service(
    container: Container = Depends(get_container),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> NotebookChatService:
    return container.get_notebook_chat_service(uow)


def get_file_ingestion_service(
    container: Container = Depends(get_container),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> FileIngestionService:
    return container.get_file_ingestion_service(uow)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    container: Container = Depends(get_container),
) -> UUID:

    # raise when JWTError or invalid raise
    credentials_exception = InvalidCredentialsException(
        "Invalid credentials or token", details={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = container.token_service.decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise InvalidCredentialsException(
            "Token expired", details={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise credentials_exception

    return UUID(user_id)
