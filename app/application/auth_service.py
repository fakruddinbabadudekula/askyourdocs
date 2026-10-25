from app.domain.refresh_token import RefreshToken, TokenStatus
from app.domain.user import User
from app.application.schemas.auth_service import LoginData, TokenData, RegisterUser
from app.application.ports.unit_of_work import AbstractUnitOfWork
from app.application.security import (
    JWTTokenService,
    PassLibPasswordHasher,
    HashLibHashService,
)
import uuid
from app.core.exceptions import (
    InvalidCredentialsException,
    RefreshTokenReUsedDetection,
    RefreshTokenValidationException,
)
from datetime import datetime, timezone

_DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$6j2nlBJCSCkFIMTYG4MQYg$hoq39+Hpcozusp8p1h5DtCxF1MjMiHncVfzkkekPipY"


class AuthService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        hash_service: HashLibHashService,
        token_service: JWTTokenService,
        password_hasher: PassLibPasswordHasher,
    ):
        self._uow = uow
        self._hash_service = hash_service
        self._token_service = token_service
        self._password_hasher = password_hasher

    def _generate_tokens(self, user_id: uuid.UUID, now: datetime) -> TokenData:
        user_id = str(user_id)
        access_token, access_expire_time = self._token_service.create_token(
            user_id, now, "access"
        )
        refresh_token, refresh_expire_time = self._token_service.create_token(
            user_id, now, "refresh"
        )
        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expire_time=access_expire_time,
            refresh_expire_time=refresh_expire_time,
        )

    async def register(self, user_data: RegisterUser) -> User:
        new_user = User.create(
            email=user_data.email,
            name=user_data.name,
            hashed_password=self._password_hasher.hash_password(user_data.password),
        )
        async with self._uow:
            await self._uow.users.save(new_user)
            await self._uow.commit()

        return new_user

    async def login(self, user_data: LoginData) -> TokenData:
        now = datetime.now(timezone.utc)
        async with self._uow:
            user = await self._uow.users.get_user_by_email(user_data.email)
            if user is None:
                self._password_hasher.verify_password(user_data.password, _DUMMY_HASH)
                raise InvalidCredentialsException(
                    "Invalid credentials email or password",
                    details={"user_email": user_data.email},
                )
            if not self._password_hasher.verify_password(
                user_data.password, user.hashed_password
            ):
                raise InvalidCredentialsException(
                    "Invalid credentials email or password",
                    details={"user_email": user_data.email},
                )

            token_data = self._generate_tokens(user.user_id, now)
            await self._uow.refresh_tokens.save(
                RefreshToken.create(
                    hashed_token=self._hash_service.hash_content(
                        token_data.refresh_token
                    ),
                    user_id=user.user_id,
                    family_id=uuid.uuid4(),
                    created_at=now,
                    expires_at=token_data.refresh_expire_time,
                )
            )
            await self._uow.commit()
            return token_data

    async def refresh(self, token: str) -> TokenData:
        now = datetime.now(timezone.utc)
        async with self._uow:
            stored_token = await self._uow.refresh_tokens.get_token_by_hash(
                self._hash_service.hash_content(token)
            )
            if stored_token is None:
                raise RefreshTokenValidationException(
                    "Invalid credentials token",
                    details={"WWW-Authenticate": "Bearer"},
                )
            if stored_token.is_revoked():
                await self._uow.refresh_tokens.revoke_all_tokens_by_family_id(
                    stored_token.family_id
                )
                await self._uow.commit()
                raise RefreshTokenReUsedDetection(
                    "Refresh token reuse detected; token revoked",
                    details={"WWW-Authenticate": "Bearer"},
                )
            if stored_token.is_expired(now):
                stored_token.mark_expired(now)
                await self._uow.refresh_tokens.update(stored_token)
                await self._uow.commit()
                raise RefreshTokenValidationException(
                    "Refresh token expired",
                    details={"WWW-Authenticate": "Bearer"},
                )

            user = await self._uow.users.get_user_by_id(stored_token.user_id)
            if not user:
                raise RefreshTokenValidationException(
                    "Invalid credentials token",
                    details={"WWW-Authenticate": "Bearer"},
                )
            token_data = self._generate_tokens(user.user_id, now)
            stored_token.revoke(now)
            await self._uow.refresh_tokens.update(stored_token)
            await self._uow.refresh_tokens.save(
                RefreshToken.create(
                    hashed_token=self._hash_service.hash_content(
                        token_data.refresh_token
                    ),
                    user_id=user.user_id,
                    family_id=stored_token.family_id,
                    created_at=now,
                    expires_at=token_data.refresh_expire_time,
                )
            )
            await self._uow.commit()
            return token_data

    async def logout(self, token: str):
        now = datetime.now(timezone.utc)
        async with self._uow:
            stored_token = await self._uow.refresh_tokens.get_token_by_hash(
                self._hash_service.hash_content(token)
            )
            if stored_token is None:
                return
            if stored_token.is_expired(now):
                stored_token.mark_expired(now)
                await self._uow.refresh_tokens.update(stored_token)
                await self._uow.commit()
                return  # idempotent, nothing to do
            if stored_token.is_revoked():
                await self._uow.refresh_tokens.revoke_all_tokens_by_family_id(
                    stored_token.family_id
                )
                await self._uow.commit()
                raise RefreshTokenReUsedDetection(
                    "Refresh token reuse detected; session revoked",
                    details={"WWW-Authenticate": "Bearer"},
                )
            stored_token.revoke(now)
            await self._uow.refresh_tokens.update(stored_token)
            await self._uow.commit()
