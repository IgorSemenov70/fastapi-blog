from uuid import uuid4

import aiofiles
import aiohttp
from aiohttp import ClientSession, InvalidURL
from bs4 import BeautifulSoup
from fastapi import Depends, UploadFile
from starlette.background import BackgroundTasks

from app.api.dependencies.database import get_repository
from app.db.repositories.post import PostRepository
from app.db.schemas.post import Post, PostCreate, PostLikeCount, ListOfPostsInResponse
from app.db.schemas.user import UserBase
from app.logging.logger import logger


async def get_all_posts(
        page: int = 0,
        limit: int = 5,
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> ListOfPostsInResponse:
    """ Сервис для постраничного вывода постов """
    posts = await post_repo.get_all(page=page, limit=limit)
    return ListOfPostsInResponse(posts=posts)


async def get_post_by_id(
        post_id: int,
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> Post:
    """ Сервис показывает детальную информацию о посте """
    return await post_repo.get_by_id(post_id=post_id)


async def create_post(
        post: PostCreate,
        author_id: int,
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> Post:
    """ Сервис для создания поста """
    return await post_repo.add(post=post, author_id=author_id)


async def like_post(
        post_id: int,
        user_id: int,
        post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> PostLikeCount:
    """ Сервис для добавления лайка на пост """
    if await post_repo.get_users_like_post(post_id=post_id, user_id=user_id):
        return await post_repo.remove_like(post_id=post_id, user_id=user_id)
    else:
        return await post_repo.add_like(post_id=post_id, user_id=user_id)


def check_user_can_modify_comment(post: Post, user: UserBase) -> bool:
    """ True если идентификаторы равны, иначе False """
    return post.author_id == user.id


async def save_files(
        user: UserBase,
        files: list[UploadFile],
        back_tasks: BackgroundTasks
) -> list[str]:
    """ Сервис для хранения media контента на сервере """
    files_list = []
    for file in files:
        if file.content_type.startswith("image"):
            file_name = f'app/media/image/{user.id}_{uuid4()}.png'
        else:
            file_name = f'app/media/video/{user.id}_{uuid4()}.mp4'
        back_tasks.add_task(_write_media, file_name, file)
        files_list.append(file_name)
    return files_list


async def _write_media(file_name: str, file: UploadFile):
    """ Записывает файл на диск """
    async with aiofiles.open(file_name, "wb") as buffer:
        data = await file.read()
        await buffer.write(data)


async def _write_preview_media(file_name: str, data: bytes):
    """ Записывает файл полученный с preview на диск """
    async with aiofiles.open(file_name, "wb") as buffer:
        await buffer.write(data)


async def get_content_by_link(
        link: str,
        user: UserBase,
        back_tasks: BackgroundTasks
) -> dict[str, str]:
    """Получение preview по ссылке"""
    if not link or not link.startswith("http"):
        return {"message": "null"}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(60)) as session:
        try:
            async with session.get(link, ssl=False) as response:
                html = await response.text()
                if response.status == 200:
                    description, image_to_url = _parse_content(html=html)
                    if image_to_url.startswith("http"):
                        preview = await _get_image_to_url(
                            session=session,
                            description=description,
                            url=image_to_url,
                            user_id=user.id,
                            back_tasks=back_tasks
                        )
                        return preview
                    else:
                        return {"description": description, "file": "Not found"}
        except InvalidURL as e:
            logger.exception(e)
            return {"message": "Invalid URL"}


async def _get_image_to_url(
        session: ClientSession,
        description: str,
        url: str,
        user_id: int,
        back_tasks: BackgroundTasks
) -> dict[str, str]:
    """ Получает фото по url для preview """
    async with session.get(url, ssl=False) as response:
        data = await response.read()
        if response.status == 200:
            file_name = f'app/media/image/{user_id}_{uuid4()}.png'
            back_tasks.add_task(_write_preview_media, file_name, data)
            return {"description": description, "file": file_name}


def _parse_content(html: str) -> tuple[str, str]:
    """ Возвращает описание и фото по ссылке """
    soup = BeautifulSoup(html, 'html.parser')

    content = soup.find("meta", property="og:description")
    if not content:
        content = soup.find(attrs={'name': 'description'})
    description = content.get("content", None) if content else "Not found"

    media_file = soup.find("meta", property="og:image")
    image = media_file.get("content", None) if media_file else "Not found"

    return description, image
