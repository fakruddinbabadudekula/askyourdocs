from fastapi import Response, Cookie
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class CookiePolicy:
    secure: bool = False
    name: str = "refresh_token"
    path: str = "/api/v1/auth"  # covers /refresh and /logout by default
    samesite: Literal["strict", "lax", "none"] = "strict"


def set_refresh_cookie(
    response: Response, token: str, expires_at: datetime, policy: CookiePolicy
) -> None:
    response.set_cookie(
        key=policy.name,
        value=token,
        expires=expires_at,
        path=policy.path,
        secure=policy.secure,
        httponly=True,
        samesite=policy.samesite,
    )


def delete_refresh_cookie(response: Response, policy: CookiePolicy) -> None:
    response.delete_cookie(
        key=policy.name,
        path=policy.path,
        secure=policy.secure,
        httponly=True,
        samesite=policy.samesite,
    )