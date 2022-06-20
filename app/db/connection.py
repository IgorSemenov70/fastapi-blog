import asyncpg
from fastapi import FastAPI

from app.config import AppSettings
from app.logging.logger import logger


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    """ Открывает соединение с бд """
    logger.info("Подключение к PostgreSQL")

    app.state.pool = await asyncpg.create_pool(
        min_size=settings.min_connection_count,
        max_size=settings.max_connection_count,
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_database,
    )
    logger.info("Открыто соединение с пулом базы данных")


async def close_db_connection(app: FastAPI) -> None:
    """ Закрывает соединение с бд """
    logger.info("Закрытие соединения с базой данных")

    await app.state.pool.close()

    logger.info("Соединение закрыто")
