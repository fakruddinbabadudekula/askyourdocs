from fastapi import APIRouter, Depends, Request, Response, status, Cookie
from app.application.auth_service import AuthService
from app.interface.api.schemas.auth import AccessTokenResponse
from app.interface.api.cookie import delete_refresh_cookie, set_refresh_cookie
from app.schemas.auth import LoginData
from app.interface.api.dependencies import get_auth_service

router = APIRouter()


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    summary="Log in with email and password",
    responses={
        401: {"description": "Invalid email or password"},
    },
)
async def login(
    payload: LoginData,
    response: Response,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessTokenResponse:
    """
    Authenticate a user and issue tokens.

    - Returns an **access token** in the response body (short-lived, used as
      `Authorization: Bearer <token>` on protected routes).
    - Sets a **refresh token** as an `HttpOnly` cookie, scoped to
      `/api/v1/auth/refresh`, valid for 7 days.
    """

    token_data = await auth_service.login(payload)
    cookie_policy = request.app.state.cookie_policy
    set_refresh_cookie(
        response,
        token_data.refresh_token,
        token_data.refresh_expire_time,
        cookie_policy,
    )
    return AccessTokenResponse(
        token=token_data.access_token, expire_at=token_data.access_expire_time
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Exchange a refresh token for a new access token",
    responses={
        401: {"description": "Missing, invalid, or expired refresh token"},
    },
)
async def refresh(
    response: Response,
    request: Request,
    token=Cookie(alias="refresh_token"),
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessTokenResponse:
    token_data = await auth_service.refresh(token)
    cookie_policy = request.app.state.cookie_policy
    set_refresh_cookie(
        response,
        token_data.refresh_token,
        token_data.refresh_expire_time,
        cookie_policy,
    )
    return AccessTokenResponse(
        token=token_data.access_token, expire_at=token_data.access_expire_time
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out the current user",
)
async def logout(
    response: Response,
    request: Request,
    token=Cookie(alias="refresh_token"),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout(token)
    cookie_policy = request.app.state.cookie_policy
    delete_refresh_cookie(response, cookie_policy)

    return
