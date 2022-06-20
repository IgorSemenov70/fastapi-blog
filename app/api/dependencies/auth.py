from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from starlette import status

from app.api.authentication import services
from app.api.dependencies.database import get_repository
from app.config import AppSettings, get_app_settings
from app.db.repositories.user import UserRepository
from app.db.schemas.user import UserBase
from app.logging.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        settings: AppSettings = Depends(get_app_settings)
) -> UserBase:
    """ Проверяет авторизован ли пользователь """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token:
        try:
            payload = services.decode_access_token(
                token=token, settings=settings)
            token_validity = payload.get("exp")
            if datetime.timestamp(datetime.utcnow()) >= token_validity:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            username: str = payload.get("username")
            if not username:
                raise credentials_exception
        except jwt.JWTError as e:
            logger.exception(e)
            raise credentials_exception
        user = await user_repo.get_by_username(username=username)
        if not user:
            raise credentials_exception
        return UserBase(id=user.id, username=user.username)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
            headers={"WWW-Authenticate": "Bearer"},
        )
