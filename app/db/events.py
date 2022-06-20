from typing import Callable

from fastapi import FastAPI

from app.config import AppSettings
from app.db.connection import close_db_connection, connect_to_db
from scripts.apply import backend, migrations


def create_start_app_handler(
    app: FastAPI,
    settings: AppSettings
) -> Callable:
    async def start_app() -> None:
        await connect_to_db(app, settings)
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))
            backend.rollback_migrations(backend.to_rollback(migrations))

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await close_db_connection(app)

    return stop_app