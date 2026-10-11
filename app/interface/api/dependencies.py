"""Module for fastapi dependencies.
contains get_current_user:which returns the current user object,
"""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError
from app.core.exceptions import InvalidCredentialsException
from app.domain.unit_of_work import AbstractUnitOfWork
from app.core.composition import get_unit_of_work
from app.core.security import decode_token
from uuid import UUID
from app.core.db import async_session_factory

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:

    # raise when JWTError or invalid raise
    credentials_exception = InvalidCredentialsException(
        "Invalid credentials or token", details={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_token(credentials.credentials)
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


def get_uow() -> AbstractUnitOfWork:
    return get_unit_of_work(async_session_factory)
