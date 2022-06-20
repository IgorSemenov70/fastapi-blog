from fastapi import Depends, HTTPException, Path
from starlette import status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_repository
from app.api.posts.services import check_user_can_modify_comment
from app.db.errors import EntityDoesNotExist
from app.db.repositories.post import PostRepository
from app.db.schemas.post import Post
from app.db.schemas.user import UserBase


async def get_post_by_id_from_path(
        post_id: int = Path(..., ge=1),
        post_repo: PostRepository = Depends(
            get_repository(PostRepository))
) -> Post:
    """ Получение поста по идентификатору из url """
    try:
        return await post_repo.get_by_id(post_id=post_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post does not exist",
        )


def check_post_modification_permissions(
        post: Post = Depends(get_post_by_id_from_path),
        user: UserBase = Depends(get_current_user),
) -> None:
    """ Проверка разрешения на удаление поста """
    if not check_user_can_modify_comment(post, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an author of this post",
        )
