from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Body,
    Response,
    BackgroundTasks
)
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.posts import check_post_modification_permissions, get_post_by_id_from_path
from app.api.posts import services
from app.api.posts.services import save_files, get_content_by_link
from app.db.repositories.post import PostRepository
from app.db.schemas.post import PostCreate, Post, PostLikeCount, ListOfPostsInResponse
from app.db.schemas.user import UserBase

post_router = APIRouter()


@post_router.get(
    "/all",
    name="posts:get-all-posts",
    status_code=status.HTTP_200_OK,
    response_model=ListOfPostsInResponse
)
async def handler_get_all_posts(
        page: int = 0,
        limit: int = 5,
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> ListOfPostsInResponse:
    """ Возвращает список постов блога с постраничной навигацией"""
    return await services.get_all_posts(
        page=page,
        limit=limit,
        post_repo=post_repo
    )


@post_router.get(
    "/{post_id}",
    name="posts:get-post",
    status_code=status.HTTP_200_OK,
    response_model=Post
)
async def handler_get_post(
        post: Post = Depends(get_post_by_id_from_path),
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> Post:
    """ Возвращает детальную информацию конкретного поста """
    return await services.get_post_by_id(
        post_id=post.id, post_repo=post_repo
    )


@post_router.post(
    "/create",
    name="posts:create-post",
    status_code=status.HTTP_201_CREATED,
    response_model=Post
)
async def handler_create_post(
        back_tasks: BackgroundTasks,
        text: str = Body(default=None),
        link: str = Body(default=None),
        files: list[UploadFile] = File(
            default=None, description="Возможность добавить несколько картинок/видео"),
        current_user: UserBase = Depends(get_current_user),
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> Post:
    """ Добавление поста в блог. Одно из полей обязательно"""
    print(files)
    if not text and not link and files == []:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One of the fields is required"
        )
    if files != []:
        files = await save_files(
            user=current_user,
            files=files,
            back_tasks=back_tasks
        )
    preview = await get_content_by_link(
        link=link,
        user=current_user,
        back_tasks=back_tasks
    )
    post_create = PostCreate(
        text=text,
        link=link,
        preview=preview,
        files=", ".join([file_name for file_name in files])
    )
    return await services.create_post(
        post=post_create,
        author_id=current_user.id,
        post_repo=post_repo
    )


@post_router.post(
    "/like/{post_id}",
    name="posts:add-like",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
    response_model=PostLikeCount
)
async def handler_add_like(
        post: Post = Depends(get_post_by_id_from_path),
        post_repo: PostRepository = Depends(get_repository(PostRepository)),
        current_user: UserBase = Depends(get_current_user)
) -> PostLikeCount:
    """ Лайк поста. Лайкнуть пост можно только 1 раз при повторном нажатии лайк снимается """
    return await services.like_post(
        user_id=current_user.id,
        post_id=post.id,
        post_repo=post_repo
    )


@post_router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="posts:delete-post",
    dependencies=[Depends(check_post_modification_permissions)],
    response_class=Response
)
async def handler_delete_post(
        post: Post = Depends(get_post_by_id_from_path),
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> None:
    """ Удаление поста. Доступно только автору поста """
    await post_repo.delete(post_id=post.id)
