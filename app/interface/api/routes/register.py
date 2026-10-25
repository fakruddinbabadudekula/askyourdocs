"""Module for register new user.
contains only register router"""

from fastapi import APIRouter, Depends
from app.application.auth_service import AuthService
from app.interface.api.schemas.auth import BaseUser, RegisterUser
from fastapi import status
from app.interface.api.dependencies import get_auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=BaseUser,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        409: {"description": "A user with this email already exists"},
    },
)
async def register(
    payload: RegisterUser, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Create a new user account.

    Passwords are hashed with Argon2 before storage; the raw password is
    never persisted or returned.
    """
    return await auth_service.register(payload)
