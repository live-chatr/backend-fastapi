from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from app.config.settings import settings

# Initialize Argon2 password hasher
password_hash = PasswordHasher(
    time_cost=settings.ARGON2_TIME_COST,  # Number of iterations
    memory_cost=settings.ARGON2_MEMORY_COST,  # Memory usage (64MB)
    parallelism=settings.ARGON2_PARALLELISM,  # Degree of parallelism
    hash_len=settings.ARGON2_HASH_LENGTH,  # Hash length
    salt_len=settings.ARGON2_SALT_LENGTH  # Salt length
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None