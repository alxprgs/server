from rich.console import Console
from rich.progress import Progress,SpinnerColumn,BarColumn,TextColumn,TimeElapsedColumn
from .core.logging import logger
from .core.tags_metadata import tags_metadata
from .core.databases.database_mongo import connect_mongo
from .core.databases.database_redis import connect_redis
from .core.databases.database_mysql import connect_mysql
from .core.root_user import setup
from .core.model import init_model
from .core.config import settings
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator

console = Console(stderr=False)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global model, mongo, mongo_db, engine, redisdb, mongodb_conn, redis_conn, mysql_conn
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TimeElapsedColumn(),
        transient=True,
        console=console
    )

    with progress:
        task = progress.add_task("Инициализация…", total=5)

        progress.update(task, advance=1, description="Подключение к MongoDB…")
        mongodb_conn, mongo_db, mongo = await connect_mongo()

        progress.update(task, advance=1, description="Подключение к Redis…")
        try:
            redis_conn, redisdb = await connect_redis()
        except Exception:
            logger.critical("Ошибка подключения к redis, отсутствует HOST")

        progress.update(task, advance=1, description="Подключение к MySQL…")
        try:
            mysql_conn, engine = await connect_mysql()
        except Exception:
            logger.critical("Ошибка подключения к mysql, отсутствует HOST")

        progress.update(task, advance=1, description="Инициализация модели…")
        model = init_model()

        if mongodb_conn:
            progress.update(task, advance=1, description="Настройка root‑пользователя…")
            await setup(db=mongo_db)
        else:
            progress.update(task, advance=1, description="Пропуск настройки root‑пользователя")

    app.state.mongodb_conn = mongodb_conn
    app.state.redis_conn = redis_conn
    app.state.mysql_conn = mysql_conn

    from .routes.processing import find_firev4
    from .routes.user import auth_user, check_auth, create_user, leave_user, set_permission, user_delete

    yield

    if mongo:
        mongo.close()
    if engine:
        await engine.dispose()
    if redisdb:
        await redisdb.close()




app = FastAPI(
    title=settings.PROJECT_NAME,
    version="Dev 11.0.0 | Build 14.04.2025",
    openapi_tags=tags_metadata,
    lifespan=lifespan
) 