from app.db.repositories.base import BaseRepository
from app.db.schemas.user import UserCreate, UserBase, UserDB


class UserRepository(BaseRepository):
    """ Репозиторий для работы с таблицей 'users' """

    async def get_by_username(self, username: str) -> UserDB:
        """ Получает пользователя по username """
        user_db = await self.connection.fetchrow(
            "SELECT id, username, hashed_password FROM users WHERE username = $1", username)
        if user_db:
            return UserDB(id=user_db[0], username=user_db[1], password=user_db[2])

    async def get_by_id(self, user_id: int) -> UserBase:
        """ Получает пользователя по id """
        user_db = await self.connection.fetchrow(
            "SELECT id, username FROM users WHERE id = $1", user_id)
        if user_db:
            return UserBase(id=user_db[0], username=user_db[1])

    async def add(self, user: UserCreate) -> UserBase:
        """ Добавляет пользователя """
        async with self.connection.transaction():
            user_db = await self.connection.fetchrow(
                "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id, username;",
                user.username, user.password)
            return UserBase(id=user_db[0], username=user_db[1])
