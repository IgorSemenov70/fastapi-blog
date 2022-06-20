from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.config import AppSettings
from app.db.repositories.user import UserRepository
from app.db.schemas.user import UserDB, UserCreate, UserBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_username(
        username: str,
        user_repo: UserRepository
) -> UserDB | None:
    """ Сервис для проверки пользователя по username """
    return await user_repo.get_by_username(username=username)


async def registration_user(
        user: UserCreate,
        user_repo: UserRepository
) -> UserBase:
    """ Сервис хеширования пароля пользователя для добавления в бд """
    user.password = pwd_context.hash(user.password)
    return await user_repo.add(user)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Сервис для проверки пароля """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        username: str,
        settings: AppSettings,
        expires_delta: Optional[timedelta] = None
) -> str:
    """ Генерирует Access Token """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode = {"exp": expire, "username": username}
    encoded_jwt = jwt.encode(
        to_encode,
        str(settings.access_secret_key),
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
        username: str,
        settings: AppSettings,
        expires_delta: Optional[timedelta] = None
) -> str:
    """ Генерирует Refresh Token """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.refresh_token_expire_minutes
        )
    to_encode = {"exp": expire, "username": username}
    encoded_jwt = jwt.encode(
        to_encode,
        str(settings.refresh_secret_key),
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str, settings: AppSettings):
    """Расшифровывает Access Token"""
    return jwt.decode(
        token,
        str(settings.access_secret_key),
        algorithms=settings.jwt_algorithm
    )


def decode_refresh_token(token: str, settings: AppSettings):
    """Расшифровывает Refresh Token"""
    return jwt.decode(
        token,
        str(settings.refresh_secret_key),
        algorithms=settings.jwt_algorithm
    )
