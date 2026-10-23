"""Module for Token creation and password hashing"""

from datetime import timedelta
from passlib.context import CryptContext
import hashlib
from jose import jwt


class HashLibHashService():
    def hash_content(self, raw):
        return hashlib.sha256(raw.encode()).hexdigest()


class PassLibPasswordHasher():
    def __init__(self, hashing_algo: str):
        self._hashing_algo = hashing_algo
        self._pwd_context = CryptContext(
            schemes=[self._hashing_algo],
            deprecated="auto",
        )

    def hash_password(self, plain_password):
        return self._pwd_context.hash(plain_password)

    def verify_password(self, plain_password, hashed_password):
        return self._pwd_context.verify(plain_password, hashed_password)


class JWTTokenService():
    def __init__(
        self,
        access_token_expiry_time_minutes: int,
        refresh_toekn_exprity_time_days: int,
        secret_key: str,
        algorithm: str,
    ):
        self._access_token_expiry_time_minutes = access_token_expiry_time_minutes
        self._refresh_toekn_exprity_time_days = refresh_toekn_exprity_time_days
        self._secret_key = secret_key
        self._algorithm = algorithm

    def create_token(self, subject, now, type):
        expire_time = (
            timedelta(minutes=self._access_token_expiry_time_minutes)
            if type == "access"
            else timedelta(days=self._refresh_toekn_exprity_time_days)
        )
        expire = now + expire_time
        payload = {
            "sub": str(subject),
            "type": type,
            "iat": now,
            "exp": expire,
        }
        return (
            jwt.encode(payload, self._secret_key, algorithm=self._algorithm),
            expire,
        )

    def decode_token(self, token):
        return jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )