from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.authentication import services
from app.api.dependencies.database import get_repository
from app.config import AppSettings, get_app_settings
from app.db.repositories.user import UserRepository
from app.db.schemas.token import Token
from app.db.schemas.user import UserLogin, UserCreate, UserBase

auth_router = APIRouter()


@auth_router.post("/token",
                  name="auth:get-tokens",
                  status_code=status.HTTP_200_OK,
                  response_model=Token,
                  include_in_schema=False
                  )
async def handler_login_for_tokens(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        settings: AppSettings = Depends(get_app_settings)
) -> Token:
    """ Авторизация """
    wrong_unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_db = await services.verify_username(
        username=form_data.username,
        user_repo=user_repo
    )
    if not user_db:
        raise wrong_unauthorized_error
    else:
        if services.verify_password(
                plain_password=form_data.password,
                hashed_password=user_db.password
        ) is False:
            raise wrong_unauthorized_error
        else:
            return Token(
                access_token=services.create_access_token(
                    username=user_db.username,
                    settings=settings
                ),
                refresh_token=services.create_refresh_token(
                    username=user_db.username,
                    settings=settings
                )
            )


@auth_router.post("/login",
                  name="auth:login",
                  status_code=status.HTTP_200_OK,
                  response_model=Token
                  )
async def handler_login(
        user_login: UserLogin,
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        settings: AppSettings = Depends(get_app_settings)
) -> Token:
    """ Авторизация """
    wrong_unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_db = await services.verify_username(
        username=user_login.username,
        user_repo=user_repo
    )
    if not user_db:
        raise wrong_unauthorized_error
    else:
        if services.verify_password(
                plain_password=user_login.password,
                hashed_password=user_db.password
        ) is False:
            raise wrong_unauthorized_error
        else:
            return Token(
                access_token=services.create_access_token(
                    username=user_db.username,
                    settings=settings
                ),
                refresh_token=services.create_refresh_token(
                    username=user_db.username,
                    settings=settings
                )
            )


@auth_router.post("/registration",
                  name="auth:registration",
                  status_code=status.HTTP_201_CREATED,
                  response_model=UserBase
                  )
async def handler_registration(
        user_create: UserCreate,
        user_repo: UserRepository = Depends(get_repository(UserRepository))
) -> UserBase:
    """ Регистрация """
    user_db = await services.verify_username(
        username=user_create.username,
        user_repo=user_repo
    )
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    return await services.registration_user(user=user_create, user_repo=user_repo)
