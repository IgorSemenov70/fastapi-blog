import json

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.db.schemas.post import PostCreate, Post, PostLikeCount


class PostRepository(BaseRepository):
    """ Репозиторий для работы с таблицей 'posts' """

    async def get_all(self, page: int = 1, limit: int = 5) -> list[Post]:
        """ Возвращает все посты """
        posts_db = await self.connection.fetch(
            "SELECT id, text, files, link, preview, author_id, like_count FROM posts LIMIT $1 OFFSET $2",
            limit, page * limit)
        return [Post(
            id=post[0],
            text=post[1],
            files=post[2],
            link=post[3],
            preview=json.loads(post[4]),
            author_id=post[5],
            like_count=post[6]
        )
            for post in posts_db
        ]

    async def get_by_id(self, post_id: int) -> Post:
        """Получает пост по id"""
        post_db = await self.connection.fetchrow(
            """SELECT id, text, files, link, preview, author_id, like_count
                    FROM posts
                    WHERE id = $1""", post_id)
        if post_db:
            return Post(
                id=post_db[0],
                text=post_db[1],
                files=post_db[2],
                link=post_db[3],
                preview=json.loads(post_db[4]),
                author_id=post_db[5],
                like_count=post_db[6],
            )
        raise EntityDoesNotExist(f"Post by id {post_id} does not exist")

    async def get_users_like_post(self, post_id: int, user_id: int) -> int | None:
        """ Получает пост по id c лайкнувшими пользователями"""
        user_likes = await self.connection.fetchval(
            """SELECT user_id FROM like_users WHERE post_id = $1 AND user_id = $2""", post_id, user_id)
        return user_likes

    async def add(self, post: PostCreate, author_id: int) -> Post:
        """ Добавление сообщения """
        async with self.connection.transaction():
            post_db = await self.connection.fetchrow(
                "INSERT INTO posts (text, files, link, preview, author_id) VALUES($1, $2, $3, $4, $5) RETURNING *",
                post.text, post.files, post.link, json.dumps(post.preview), author_id)
            return Post(
                id=post_db[0],
                text=post_db[1],
                files=post_db[2],
                link=post_db[3],
                preview=json.loads(post_db[4]),
                like_count=post_db[5],
                author_id=post_db[6]
            )

    async def add_like(self, post_id: int, user_id: int) -> PostLikeCount:
        """ Увеличивает кол-во лайков на 1 """
        async with self.connection.transaction():
            await self.connection.execute(
                "INSERT INTO like_users (user_id, post_id) VALUES ($1, $2)", user_id, post_id)
            like_count = await self.connection.fetchval(
                "UPDATE posts SET like_count = like_count + 1 WHERE id = $1 RETURNING like_count", post_id)
            return PostLikeCount(like_count=like_count)

    async def remove_like(self, post_id: int, user_id: int) -> PostLikeCount:
        """ Уменьшает кол-во лайков на 1"""
        async with self.connection.transaction():
            await self.connection.execute(
                "DELETE FROM like_users WHERE post_id = $1 AND user_id = $2", post_id, user_id)
            like_count = await self.connection.fetchval(
                "UPDATE posts SET like_count = like_count - 1 WHERE id = $1 RETURNING like_count", post_id)
            return PostLikeCount(like_count=like_count)

    async def delete(self, post_id: int) -> None:
        """ Удаление сообщения """
        async with self.connection.transaction():
            await self.connection.execute("DELETE FROM posts WHERE id = $1", post_id)
